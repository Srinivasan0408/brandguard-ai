import io
import pytest
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.database import db
from backend.app.auth import hash_password, verify_and_maybe_migrate_password, hash_password_legacy_sha256
from backend.app.engine.visual import (
    extract_ocr_text,
    analyze_extracted_image_text,
    calculate_contrast_ratio,
    relative_luminance,
    analyze_visual_asset
)

client = TestClient(app)

# -------------------------------------------------------------
# 1. ARGON2ID PASSWORD SECURITY & MIGRATION TESTS
# -------------------------------------------------------------

def test_argon2id_hashing_and_verification():
    """Verify newly hashed passwords use Argon2id format and verify securely."""
    password = "SuperSecretPassword2026!"
    hashed = hash_password(password)

    # Must start with $argon2id
    assert hashed.startswith("$argon2id$")
    assert "m=65536,t=3,p=4" in hashed

    # Valid password verification
    is_valid, needs_migration, new_hash = verify_and_maybe_migrate_password(password, hashed)
    assert is_valid is True
    assert needs_migration is False
    assert new_hash is None

    # Invalid password verification
    is_valid_wrong, _, _ = verify_and_maybe_migrate_password("WrongPassword123!", hashed)
    assert is_valid_wrong is False

def test_legacy_sha256_login_migrates_automatically_to_argon2id():
    """Verify legacy SHA-256 user logins succeed and automatically upgrade to Argon2id in the database."""
    # Create or ensure user with legacy hash
    legacy_pass = "password123"
    legacy_hash = hash_password_legacy_sha256(legacy_pass)

    test_username = "legacy_test_user"
    existing = db.get_user_by_username(test_username)
    if not existing:
        db.create_user({
            "username": test_username,
            "email": "legacy@novatech.internal",
            "full_name": "Legacy User",
            "role": "creator",
            "organization_id": "org-novatech",
            "password_hash": legacy_hash
        })
    else:
        db.update_user_password_hash(existing["id"], legacy_hash)

    # Initial state: hash is legacy SHA-256 (64 hex characters)
    user_before = db.get_user_by_username(test_username)
    assert user_before["password_hash"] == legacy_hash
    assert not user_before["password_hash"].startswith("$argon2")

    # Login with legacy credentials
    res = client.post("/api/auth/login", json={
        "username": test_username,
        "password": legacy_pass
    })
    assert res.status_code == 200
    token_data = res.json()
    assert "access_token" in token_data

    # Database state: hash MUST now be upgraded to Argon2id automatically
    user_after = db.get_user_by_username(test_username)
    assert user_after["password_hash"].startswith("$argon2id$")
    assert user_after["password_hash"] != legacy_hash

    # Subsequent login with new Argon2id hash succeeds
    res2 = client.post("/api/auth/login", json={
        "username": test_username,
        "password": legacy_pass
    })
    assert res2.status_code == 200

def test_new_user_creation_stores_argon2id_directly():
    """Verify that when an admin creates a new user, password is saved using Argon2id."""
    # Login as admin
    login_res = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert login_res.status_code == 200
    admin_token = login_res.json()["access_token"]

    new_username = "new_developer_argon"
    if db.get_user_by_username(new_username):
        user = db.get_user_by_username(new_username)
        assert user["password_hash"].startswith("$argon2id$")
    else:
        create_res = client.post("/api/auth/users", json={
            "username": new_username,
            "email": "argon.dev@novatech.internal",
            "full_name": "Argon Developer",
            "role": "creator",
            "organization_id": "org-novatech",
            "password": "ArgonSecurePassword999!"
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert create_res.status_code == 201

        created_user = db.get_user_by_username(new_username)
        assert created_user["password_hash"].startswith("$argon2id$")


# -------------------------------------------------------------
# 2. ORGANIZATION-LEVEL DATA ISOLATION TESTS
# -------------------------------------------------------------

def test_multi_tenant_organization_isolation():
    """
    Verify strict boundary enforcement between organizations:
    - User in org-apex cannot read or approve content in org-novatech (403 Forbidden)
    - Role restrictions: creators cannot manage brand rules or facts
    - Scoped listing respects organization identity
    """
    # 1. Login as NovaTech creator and create a content item
    novatech_login = client.post("/api/auth/login", json={"username": "creator", "password": "creator123"})
    assert novatech_login.status_code == 200
    nova_token = novatech_login.json()["access_token"]

    create_item_res = client.post("/api/reviews", json={
        "brand_id": "brand-novatech-001",
        "title": "Confidential NovaTech Roadmap Brief",
        "content_type": "marketing",
        "channel": "Website",
        "raw_content": "NovaTech Pro cloud infrastructure is enterprise security powered by NovaTech. Terms & conditions apply."
    }, headers={"Authorization": f"Bearer {nova_token}"})
    assert create_item_res.status_code == 201
    nova_item = create_item_res.json()
    item_id = nova_item["id"]
    assert nova_item.get("organization_id") == "org-novatech"

    # 2. Login as Apex admin (a different organization)
    apex_login = client.post("/api/auth/login", json={"username": "apex_admin", "password": "admin123"})
    assert apex_login.status_code == 200
    apex_token = apex_login.json()["access_token"]
    assert apex_login.json()["user"]["organization_id"] == "org-apex"

    # 3. Apex admin attempts to READ NovaTech content -> MUST BE REJECTED with 403 Forbidden
    cross_read_res = client.get(f"/api/reviews/{item_id}", headers={"Authorization": f"Bearer {apex_token}"})
    assert cross_read_res.status_code == 403
    assert "another organization" in cross_read_res.json()["detail"].lower() or "forbidden" in cross_read_res.json()["detail"].lower()

    # 4. Apex admin attempts to APPROVE NovaTech content -> MUST BE REJECTED with 403 Forbidden
    cross_approve_res = client.post(f"/api/reviews/{item_id}/approve", json={
        "actor_name": "Apex Attacker",
        "actor_role": "admin",
        "comments": "Malicious cross-org approval attempt"
    }, headers={"Authorization": f"Bearer {apex_token}"})
    assert cross_approve_res.status_code == 403

    # 5. Apex admin attempts to view NovaTech brand guidelines -> 403 Forbidden
    cross_brand_res = client.get("/api/brands/brand-novatech-001", headers={"Authorization": f"Bearer {apex_token}"})
    assert cross_brand_res.status_code == 403

    # 6. Creator role restriction: Creator cannot update brand guidelines
    creator_brand_edit = client.put("/api/brands/brand-novatech-001", json={
        "description": "Unauthorized creator edit of guidelines"
    }, headers={"Authorization": f"Bearer {nova_token}"})
    assert creator_brand_edit.status_code == 403
    assert "Only administrators" in creator_brand_edit.json()["detail"]


# -------------------------------------------------------------
# 3. OCR-BASED VISUAL BRAND ANALYSIS & CONTRAST TESTS
# -------------------------------------------------------------

def test_ocr_visual_brand_rule_violation_detection():
    """Verify image text analysis detects prohibited terminology and unapproved claims."""
    brand = {
        "id": "brand-novatech-001",
        "name": "NovaTech",
        "prohibited_terminology": ["cheap", "unbreakable", "foolproof", "hack-proof", "100% secure"],
        "approved_terminology": ["NovaTech Pro"],
        "formatting_preferences": {"brand_colors": ["#06b6d4", "#14b8a6", "#0f172a", "#1e293b", "#ffffff"]}
    }

    # Test text containing violations
    non_compliant_text = "Get the all-new Nova Pro today for a cheap price with unbreakable protection!"
    findings = analyze_extracted_image_text(non_compliant_text, brand, ocr_confidence=88.5)

    assert len(findings) >= 2
    triggers = [f["trigger_text"].lower() for f in findings]
    assert "cheap" in triggers
    assert "unbreakable" in triggers

    # Test clean compliant text
    compliant_text = "Introducing NovaTech Pro, engineered for resilient enterprise infrastructure."
    clean_findings = analyze_extracted_image_text(compliant_text, brand, ocr_confidence=92.0)
    assert len(clean_findings) == 0

def test_wcag_22_contrast_calculation():
    """Verify relative luminance and WCAG 2.2 AA contrast ratio calculations."""
    black = (0, 0, 0)
    white = (255, 255, 255)
    ratio = calculate_contrast_ratio(white, black)
    # White vs Black is 21:1
    assert ratio == 21.0

    # Low contrast pair (e.g. #94a3b8 and #cbd5e1)
    rgb1 = (148, 163, 184)
    rgb2 = (203, 213, 225)
    low_ratio = calculate_contrast_ratio(rgb1, rgb2)
    assert low_ratio < 4.5  # Below WCAG 2.2 AA threshold for body text

def test_visual_analysis_graceful_ocr_fallback():
    """Verify that when analyzing an image in an environment without Tesseract CLI, the engine falls back safely."""
    # Create a small valid test PNG image in-memory
    img = Image.new("RGB", (800, 600), color="#06b6d4")
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 100, 700, 500], fill="#0f172a")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    brand = db.get_brand("brand-novatech-001")
    analysis = analyze_visual_asset(
        image_bytes=img_bytes,
        file_name="test_banner.png",
        brand=brand,
        alt_text="A high contrast test marketing banner for NovaTech Pro"
    )

    # Core deterministic fields must always be present
    assert analysis["dimensions"]["width"] == 800
    assert analysis["dimensions"]["height"] == 600
    assert analysis["format"] == "PNG"
    assert len(analysis["dominant_colors"]) > 0
    assert analysis["palette_compliance_score"] >= 0.0
    assert analysis["contrast_ratio"] is not None
    assert "checks" in analysis
    assert len(analysis["checks"]) >= 4

    # OCR status must be cleanly handled (either available or explicit fallback note)
    assert "ocr_available" in analysis
    assert "ocr_status_note" in analysis
    if not analysis["ocr_available"]:
        assert "not detected" in analysis["ocr_status_note"].lower() or "fallback" in analysis["ocr_status_note"].lower()


# -------------------------------------------------------------
# 4. WORKFLOW HARDENING, CRITICAL VIOLATIONS & DEDUPLICATION
# -------------------------------------------------------------

def test_critical_violation_blocks_approval():
    """Verify that open critical violations block approval with HTTP 400."""
    login_res = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post("/api/reviews", json={
        "brand_id": "brand-novatech-001",
        "title": "Critical Price Violation Test",
        "content_type": "social",
        "channel": "LinkedIn",
        "raw_content": "Get the NovaTech Pro today for only ₹5,999!",
        "image_alt_text": "Product banner"
    }, headers=headers)
    assert create_res.status_code == 201
    item = create_res.json()
    item_id = item["id"]

    sub_res = client.post(f"/api/reviews/{item_id}/submit", json={
        "actor_name": "Admin",
        "actor_role": "admin"
    }, headers=headers)
    assert sub_res.status_code == 200

    approve_res = client.post(f"/api/reviews/{item_id}/approve", json={
        "actor_name": "Chief Governance Administrator",
        "actor_role": "admin",
        "comments": "Attempting approval"
    }, headers=headers)

    assert approve_res.status_code == 400
    assert "critical violation" in approve_res.json()["detail"].lower()


def test_reviewer_reject_workflow():
    """Verify authorized reviewers can reject non-compliant submissions."""
    login_res = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post("/api/reviews", json={
        "brand_id": "brand-novatech-001",
        "title": "Reject Workflow Test",
        "content_type": "social",
        "channel": "LinkedIn",
        "raw_content": "Unacceptable content that fails all legal criteria.",
        "image_alt_text": "Banner"
    }, headers=headers)
    item_id = create_res.json()["id"]

    client.post(f"/api/reviews/{item_id}/submit", json={"actor_name": "Admin", "actor_role": "admin"}, headers=headers)

    reject_res = client.post(f"/api/reviews/{item_id}/reject", json={
        "actor_name": "Chief Governance Administrator",
        "actor_role": "admin",
        "comments": "Violates trademark guidelines and legal standards."
    }, headers=headers)

    assert reject_res.status_code == 200
    rejected_item = reject_res.json()
    assert rejected_item["status"] == "rejected"
    assert any(evt["event_type"] == "rejected" for evt in rejected_item["approval_history"])


def test_creator_cannot_approve_own_content():
    """Verify separation of duties: creator cannot approve their own submission."""
    creator_login = client.post("/api/auth/login", json={"username": "creator", "password": "creator123"})
    creator_token = creator_login.json()["access_token"]
    creator_headers = {"Authorization": f"Bearer {creator_token}"}

    create_res = client.post("/api/reviews", json={
        "brand_id": "brand-novatech-001",
        "title": "Separation of Duties Test",
        "content_type": "social",
        "channel": "LinkedIn",
        "raw_content": "Compliant content crafted by creator.",
        "image_alt_text": "Compliant banner"
    }, headers=creator_headers)
    item_id = create_res.json()["id"]

    client.post(f"/api/reviews/{item_id}/submit", json={"actor_name": "Alice Creator", "actor_role": "creator"}, headers=creator_headers)

    approve_res = client.post(f"/api/reviews/{item_id}/approve", json={
        "actor_name": "Alice Creator",
        "actor_role": "creator"
    }, headers=creator_headers)

    assert approve_res.status_code == 403


def test_draft_deduplication_prevention():
    """Verify submitting or saving the same draft updates existing record instead of creating duplicates."""
    draft_payload = {
        "brand_id": "brand-novatech-001",
        "title": "Idempotent Draft Test",
        "content_type": "social",
        "channel": "X / Twitter",
        "campaign_ref": "IDEMPOTENT-TEST-001",
        "raw_content": "Draft version 1 text",
        "image_alt_text": "Alt 1"
    }

    res1 = client.post("/api/reviews", json=draft_payload)
    assert res1.status_code == 201
    item1 = res1.json()

    draft_payload["raw_content"] = "Draft version 2 updated text"
    res2 = client.post("/api/reviews", json=draft_payload)
    assert res2.status_code == 201
    item2 = res2.json()

    assert item1["id"] == item2["id"]
    assert "Draft version 2 updated text" in item2["raw_content"]


def test_governance_insights_multi_tenant_and_percentage_sum():
    """Verify insights are isolated by organization and category distribution percentages total approximately 100%."""
    ins_novatech = db.get_governance_insights(organization_id="org-novatech")
    assert ins_novatech["total_content_items"] >= 1
    if ins_novatech["total_findings_detected"] > 0:
        total_pct = sum(cat["percentage"] for cat in ins_novatech["category_distribution"])
        assert round(total_pct, 1) == 100.0

    ins_apex = db.get_governance_insights(organization_id="org-apex")
    assert ins_apex["total_content_items"] >= 1
    assert ins_apex["approved_count"] >= 1
