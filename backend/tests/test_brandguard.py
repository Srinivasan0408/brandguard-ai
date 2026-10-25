import pytest
import os
import io
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.database import db
from backend.app.config import settings

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown():
    # Reset database before tests
    db.reset_database()
    yield

def test_1_prohibited_term_detected():
    """TEST 1: A post contains a prohibited term. Expected: A terminology finding is returned."""
    payload = {
        "brand_id": "brand-novatech-001",
        "title": "Campaign with prohibited term",
        "content_type": "social",
        "channel": "X / Twitter",
        "raw_content": "Get the new hardware today for a cheap price!",
        "image_alt_text": "Product display banner",
        "created_by": "Test Creator"
    }
    response = client.post("/api/reviews", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["latest_review"] is not None
    findings = data["latest_review"]["findings"]
    
    # Check terminology finding
    term_findings = [f for f in findings if f["category"] == "terminology" and "cheap" in f["excerpt"].lower()]
    assert len(term_findings) >= 1
    assert "cheap" in term_findings[0]["excerpt"].lower()
    assert term_findings[0]["severity"] == "high"

def test_2_approved_price_mismatch():
    """TEST 2: The approved price is ₹4,999, but submitted content states ₹5,999. Expected: A potential approved-fact mismatch is returned."""
    payload = {
        "brand_id": "brand-novatech-001",
        "title": "Pricing Announcement",
        "content_type": "social",
        "channel": "LinkedIn",
        "raw_content": "NovaTech Pro is now available for just ₹5,999 on our portal.",
        "image_alt_text": "Price card showing product",
        "created_by": "Test Creator"
    }
    response = client.post("/api/reviews", json=payload)
    assert response.status_code == 201
    data = response.json()
    findings = data["latest_review"]["findings"]

    # Check fact contradiction finding
    fact_findings = [f for f in findings if f["category"] == "facts"]
    assert len(fact_findings) >= 1
    price_finding = fact_findings[0]
    assert "₹5,999" in price_finding["excerpt"]
    assert price_finding["severity"] == "critical"
    assert "₹4,999" in price_finding["explanation"]
    assert "₹4,999" in price_finding["recommended_correction"]

def test_3_promotional_claim_warning():
    """TEST 3: A post contains '100% guaranteed results' and policy prohibits unsupported guarantees. Expected: A promotional-claim warning is returned."""
    payload = {
        "brand_id": "brand-novatech-001",
        "title": "Guaranteed results post",
        "content_type": "marketing",
        "channel": "Email",
        "raw_content": "Our solution delivers 100% guaranteed results with zero downtime.",
        "image_alt_text": "Performance graph",
        "created_by": "Test Creator"
    }
    response = client.post("/api/reviews", json=payload)
    assert response.status_code == 201
    data = response.json()
    findings = data["latest_review"]["findings"]

    claim_findings = [f for f in findings if f["category"] == "claims"]
    assert len(claim_findings) >= 1
    assert any("guaranteed results" in f["excerpt"].lower() for f in claim_findings)

def test_4_compliant_content_no_false_violations():
    """TEST 4: Content follows all configured rules. Expected: No false violation is generated for those rules."""
    payload = {
        "brand_id": "brand-novatech-001",
        "title": "Fully Compliant Post",
        "content_type": "social",
        "channel": "LinkedIn",
        "raw_content": (
            "Introducing NovaTech Pro, engineered for resilient enterprise infrastructure. "
            "Available now starting at ₹4,999 with 12 months hardware warranty. "
            "Enterprise security powered by NovaTech. Terms & conditions apply."
        ),
        "image_alt_text": "High-resolution photo of the NovaTech Pro server chassis",
        "created_by": "Senior Copywriter"
    }
    response = client.post("/api/reviews", json=payload)
    assert response.status_code == 201
    data = response.json()
    findings = data["latest_review"]["findings"]

    # Should have no critical or high violations
    severe_findings = [f for f in findings if f["severity"] in ("critical", "high")]
    assert len(severe_findings) == 0

def test_5_edit_content_and_rerun_review():
    """TEST 5: A user edits content and reruns the review. Expected: The new review reflects the edited content."""
    # 1. Create content with violation
    create_res = client.post("/api/reviews", json={
        "brand_id": "brand-novatech-001",
        "title": "Draft Post",
        "content_type": "social",
        "channel": "X",
        "raw_content": "Get the cheap version of NovaTech Pro for ₹5,999.",
        "image_alt_text": "Banner",
        "created_by": "Creator"
    })
    item_id = create_res.json()["id"]
    assert create_res.json()["latest_review"]["findings_count"] >= 2

    # 2. Revise content to fix violations
    revise_res = client.post(f"/api/reviews/{item_id}/revise", json={
        "content_text": "Get the cost-effective NovaTech Pro starting at ₹4,999. Enterprise security powered by NovaTech. Terms & conditions apply.",
        "image_alt_text": "Clean banner",
        "change_summary": "Replaced 'cheap' with 'cost-effective' and corrected price to ₹4,999",
        "actor_name": "Creator",
        "actor_role": "creator"
    })
    assert revise_res.status_code == 200
    revised = revise_res.json()
    assert revised["current_revision"] == 2
    # Critical violations should now be 0
    assert revised["latest_review"]["critical_count"] == 0

def test_6_submit_for_review_changes_status():
    """TEST 6: A creator submits content for review. Expected: The review status changes to In Review."""
    create_res = client.post("/api/reviews", json={
        "brand_id": "brand-novatech-001",
        "title": "Ready for Review Post",
        "content_type": "website",
        "channel": "Blog",
        "raw_content": "Enterprise security with NovaTech Pro at ₹4,999.",
        "created_by": "Creator"
    })
    item_id = create_res.json()["id"]
    assert create_res.json()["status"] == "draft"

    submit_res = client.post(f"/api/reviews/{item_id}/submit", json={
        "actor_name": "Alice Creator",
        "actor_role": "creator",
        "comments": "Please review this blog post for tomorrow's launch."
    })
    assert submit_res.status_code == 200
    assert submit_res.json()["status"] == "in_review"

def test_7_reviewer_requests_changes():
    """TEST 7: An authorised reviewer requests changes. Expected: The status changes and the reviewer comment is recorded."""
    # Create and submit
    c_res = client.post("/api/reviews", json={
        "brand_id": "brand-novatech-001",
        "title": "Campaign Post",
        "content_type": "social",
        "channel": "LinkedIn",
        "raw_content": "NovaTech Pro launched.",
        "created_by": "Creator"
    })
    item_id = c_res.json()["id"]
    client.post(f"/api/reviews/{item_id}/submit", json={"actor_name": "Alice", "actor_role": "creator"})

    # Reviewer requests changes
    req_res = client.post(f"/api/reviews/{item_id}/request-changes", json={
        "actor_name": "Bob Reviewer",
        "actor_role": "reviewer",
        "comments": "Please add the approved disclaimer and check pricing details."
    })
    assert req_res.status_code == 200
    data = req_res.json()
    assert data["status"] == "changes_requested"
    assert len(data["comments"]) >= 1
    assert data["comments"][-1]["comment_text"] == "Please add the approved disclaimer and check pricing details."

def test_8_revisions_preserved_and_inspectable():
    """TEST 8: The creator submits a revised version. Expected: The revision is preserved and can be inspected."""
    c_res = client.post("/api/reviews", json={
        "brand_id": "brand-novatech-001",
        "title": "Versioned Post",
        "content_type": "social",
        "channel": "LinkedIn",
        "raw_content": "Version 1 text",
        "created_by": "Creator"
    })
    item_id = c_res.json()["id"]

    # Revise
    client.post(f"/api/reviews/{item_id}/revise", json={
        "content_text": "Version 2 revised text with improvements",
        "change_summary": "Added clarity to opening",
        "actor_name": "Creator",
        "actor_role": "creator"
    })

    # Fetch item
    get_res = client.get(f"/api/reviews/{item_id}")
    item = get_res.json()
    assert len(item["revisions"]) == 2
    assert item["revisions"][0]["revision_number"] == 1
    assert item["revisions"][0]["content_text"] == "Version 1 text"
    assert item["revisions"][1]["revision_number"] == 2
    assert item["revisions"][1]["content_text"] == "Version 2 revised text with improvements"

def test_9_reviewer_approves_revised_content():
    """TEST 9: An authorised reviewer approves the revised content. Expected: Final status becomes Approved and decision recorded."""
    c_res = client.post("/api/reviews", json={
        "brand_id": "brand-novatech-001",
        "title": "Post for Approval",
        "content_type": "social",
        "channel": "LinkedIn",
        "raw_content": "NovaTech Pro enterprise security at ₹4,999.",
        "created_by": "Creator"
    })
    item_id = c_res.json()["id"]
    client.post(f"/api/reviews/{item_id}/submit", json={"actor_name": "Alice", "actor_role": "creator"})

    # Approve
    approve_res = client.post(f"/api/reviews/{item_id}/approve", json={
        "actor_name": "Bob Senior Brand Reviewer",
        "actor_role": "reviewer",
        "comments": "Approved for public publishing."
    })
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "approved"
    events = approve_res.json()["approval_history"]
    assert any(e["event_type"] == "approved" and e["actor_role"] == "reviewer" for e in events)

def test_10_unauthorised_user_rejected_from_approval():
    """TEST 10: An unauthorised user attempts an approval action. Expected: The operation is rejected."""
    c_res = client.post("/api/reviews", json={
        "brand_id": "brand-novatech-001",
        "title": "Post to test unauthorized approval",
        "content_type": "social",
        "channel": "LinkedIn",
        "raw_content": "Content here",
        "created_by": "Creator"
    })
    item_id = c_res.json()["id"]
    client.post(f"/api/reviews/{item_id}/submit", json={"actor_name": "Alice", "actor_role": "creator"})

    # Attempt approve as creator
    unauth_res = client.post(f"/api/reviews/{item_id}/approve", json={
        "actor_name": "Malicious Creator",
        "actor_role": "creator",
        "comments": "Self-approving my own post"
    })
    assert unauth_res.status_code == 403
    assert "Forbidden" in unauth_res.json()["detail"]

def test_11_file_upload_validation_rejected_safely():
    """TEST 11: A file has an unsupported extension or exceeds size limit. Expected: Upload rejected safely."""
    # 1. Unsupported extension (.exe or .zip)
    fake_exe = io.BytesIO(b"MZ\x90\x00\x03\x00\x00\x00")
    res_exe = client.post("/api/reviews/upload", files={"file": ("malicious.exe", fake_exe, "application/octet-stream")})
    assert res_exe.status_code == 400
    assert "Unsupported file format" in res_exe.json()["detail"]

    # 2. Valid .txt file
    valid_txt = io.BytesIO(b"NovaTech Pro launch copy at Rs 4,999.")
    res_valid = client.post("/api/reviews/upload", files={"file": ("campaign.txt", valid_txt, "text/plain")})
    assert res_valid.status_code == 200
    assert res_valid.json()["filename"] == "campaign.txt"
    assert "NovaTech Pro" in res_valid.json()["content_text"]

def test_12_no_llm_key_deterministic_fallback_and_mode_indication():
    """TEST 12: The application runs without an external LLM API key. Expected: Deterministic review features remain operational and UI clearly identifies analysis mode."""
    # Ensure health endpoint reports analysis mode
    health_res = client.get("/health")
    assert health_res.status_code == 200
    h_data = health_res.json()
    assert "review_engine" in h_data
    assert "analysis_mode" in h_data["review_engine"]

    # Review still runs deterministically
    review_res = client.post("/api/reviews", json={
        "brand_id": "brand-novatech-001",
        "title": "Offline Review Test",
        "content_type": "social",
        "channel": "X",
        "raw_content": "NovaTech Pro for ₹4,999 is cheap.",
        "created_by": "Tester"
    })
    assert review_res.status_code == 201
    run = review_res.json()["latest_review"]
    assert run["analysis_mode"] == "deterministic"
    assert run["findings_count"] >= 1
