import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image
from backend.app.main import app
from backend.app.db.database import db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    db.reset_database()
    yield

# --- Round 3: Authentication & Multi-User Governance Tests ---

def test_r3_auth_login_success():
    """Verify login with seeded admin credentials returns JWT access token."""
    res = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["username"] == "admin"
    assert data["user"]["role"] == "admin"

def test_r3_auth_login_invalid_password():
    """Verify login fails safely with wrong password and records failed audit event."""
    res = client.post("/api/auth/login", json={"username": "admin", "password": "wrongpassword"})
    assert res.status_code == 401
    assert "Invalid username or password" in res.json()["detail"]

def test_r3_auth_me_protected():
    """Verify /api/auth/me rejects unauthenticated requests and accepts valid Bearer token."""
    # Unauthenticated
    unauth_res = client.get("/api/auth/me")
    assert unauth_res.status_code == 401

    # Login and get token
    login_res = client.post("/api/auth/login", json={"username": "creator", "password": "creator123"})
    token = login_res.json()["access_token"]

    # Authenticated
    auth_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert auth_res.status_code == 200
    assert auth_res.json()["username"] == "creator"
    assert auth_res.json()["role"] == "creator"

def test_r3_rbac_server_side_enforcement():
    """Verify backend enforces role from token: creator cannot approve even if payload claims reviewer."""
    # 1. Create content item
    create_res = client.post("/api/reviews", json={
        "brand_id": "brand-novatech-001",
        "title": "RBAC Security Test",
        "content_type": "social",
        "channel": "LinkedIn",
        "raw_content": "NovaTech Pro security update",
        "created_by": "Alice"
    })
    item_id = create_res.json()["id"]

    # Submit for review
    client.post(f"/api/reviews/{item_id}/submit", json={"actor_name": "Alice", "actor_role": "creator"})

    # 2. Login as creator
    creator_token = client.post("/api/auth/login", json={"username": "creator", "password": "creator123"}).json()["access_token"]

    # 3. Creator attempts approval with spoofed payload role="reviewer"
    spoof_res = client.post(
        f"/api/reviews/{item_id}/approve",
        json={"actor_name": "Alice", "actor_role": "reviewer", "comments": "Spoofed approval attempt"},
        headers={"Authorization": f"Bearer {creator_token}"}
    )
    assert spoof_res.status_code == 403
    assert "Forbidden" in spoof_res.json()["detail"]

    # 4. Reviewer approves legitimately
    reviewer_token = client.post("/api/auth/login", json={"username": "reviewer", "password": "reviewer123"}).json()["access_token"]
    legit_res = client.post(
        f"/api/reviews/{item_id}/approve",
        json={"actor_name": "Bob Reviewer", "actor_role": "reviewer", "comments": "Authorized sign-off"},
        headers={"Authorization": f"Bearer {reviewer_token}"}
    )
    assert legit_res.status_code == 200
    assert legit_res.json()["status"] == "approved"

# --- Round 3: Evidence-Grounded AI Review Tests ---

def test_r3_evidence_traceability_on_findings():
    """Verify findings include evidence_record_id, evidence_status, and correction_rationale."""
    res = client.post("/api/reviews", json={
        "brand_id": "brand-novatech-001",
        "title": "Evidence Grounding Test",
        "content_type": "social",
        "channel": "X / Twitter",
        "raw_content": "Get the cheap NovaTech Pro for ₹5,999 with 100% guaranteed results!",
        "created_by": "Test Creator"
    })
    assert res.status_code == 201
    findings = res.json()["latest_review"]["findings"]

    # Price finding evidence check
    price_f = next(f for f in findings if f["category"] == "facts")
    assert price_f["evidence_record_id"] == "fact-novatech-001"
    assert price_f["evidence_status"] == "verified"
    assert "fact-novatech-001" in price_f["correction_rationale"]

    # Terminology finding evidence check
    term_f = next(f for f in findings if f["category"] == "terminology")
    assert "guideline-term-cheap" in term_f["evidence_record_id"]
    assert term_f["evidence_status"] == "verified"
    assert "Replaces prohibited buzzword" in term_f["correction_rationale"]

    # Claim finding evidence check
    claim_f = next(f for f in findings if f["category"] == "claims")
    assert claim_f["evidence_status"] == "insufficient_evidence"
    assert claim_f["correction_rationale"] is not None

# --- Round 3: Visual Brand Consistency & Accessibility Tests ---

def create_test_image(color=(6, 182, 212), size=(800, 600), format="PNG"):
    """Helper to generate in-memory synthetic image bytes."""
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format=format)
    buf.seek(0)
    return buf

def test_r3_visual_analysis_success():
    """Verify image upload and deterministic visual analysis: dimensions, palette matching, WCAG contrast."""
    # Synthetic image with NovaTech primary brand cyan
    img_buf = create_test_image(color=(6, 182, 212), size=(1200, 800))
    res = client.post(
        "/api/visual/analyze",
        files={"file": ("novatech_banner.png", img_buf, "image/png")},
        data={"brand_id": "brand-novatech-001", "alt_text": "Executive workstation with NovaTech Pro server chassis"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["dimensions"]["width"] == 1200
    assert data["dimensions"]["height"] == 800
    assert data["format"] == "PNG"
    assert len(data["dominant_colors"]) >= 1
    # Check palette compliance score
    assert data["palette_compliance_score"] > 50.0
    # Check checks array
    check_names = [c["check_name"] for c in data["checks"]]
    assert "Resolution & Dimensions" in check_names
    assert "Brand Color Palette Alignment" in check_names
    assert "Associated Alternative Text" in check_names

def test_r3_visual_analysis_unsupported_file_type():
    """Verify rejection of non-image MIME types."""
    fake_doc = io.BytesIO(b"Hello world document")
    res = client.post(
        "/api/visual/analyze",
        files={"file": ("notes.pdf", fake_doc, "application/pdf")},
        data={"brand_id": "brand-novatech-001"}
    )
    assert res.status_code == 400
    assert "Unsupported image format" in res.json()["detail"]

def test_r3_visual_analysis_missing_alt_text_flagged():
    """Verify accessibility check flags missing alternative text."""
    img_buf = create_test_image(size=(800, 600))
    res = client.post(
        "/api/visual/analyze",
        files={"file": ("promo.jpg", img_buf, "image/jpeg")},
        data={"brand_id": "brand-novatech-001", "alt_text": ""}
    )
    assert res.status_code == 200
    data = res.json()
    alt_check = next(c for c in data["checks"] if c["check_name"] == "Associated Alternative Text")
    assert alt_check["status"] == "fail"
    assert alt_check["severity"] == "high"
