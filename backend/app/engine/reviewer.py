import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from ..db.database import db
from .terminology import check_terminology
from .facts import check_approved_facts
from .claims import check_promotional_claims
from .tone import check_tone_heuristics
from .accessibility import check_accessibility
from .requirements import check_required_elements
from .llm_helper import llm_helper

SEVERITY_ORDER = {
    "critical": 1,
    "high": 2,
    "medium": 3,
    "low": 4,
    "informational": 5
}

async def run_review(
    content_id: str,
    content_text: str,
    brand_id: str,
    image_alt_text: Optional[str] = None,
    channel: str = "general",
    revision_number: int = 1
) -> Dict[str, Any]:
    brand = db.get_brand(brand_id)
    if not brand:
        # Fallback to default brand if not found
        brands = db.list_brands()
        brand = brands[0] if brands else {}

    facts = db.list_facts(brand.get("id"))

    findings: List[Dict[str, Any]] = []

    # 1. Terminology Checks
    findings.extend(check_terminology(content_text, brand))

    # 2. Approved Facts Checks
    findings.extend(check_approved_facts(content_text, facts))

    # 3. Promotional Claims Checks
    findings.extend(check_promotional_claims(content_text, brand))

    # 4. Tone Heuristic Checks
    findings.extend(check_tone_heuristics(content_text, brand))

    # 5. Accessibility Checks
    findings.extend(check_accessibility(content_text, image_alt_text, channel))

    # 6. Required Disclaimers & Elements
    findings.extend(check_required_elements(content_text, brand))

    # 7. Optional LLM refinement (if configured)
    analysis_mode = "deterministic"
    if llm_helper.is_available():
        llm_findings = await llm_helper.analyze_tone_and_refine(content_text, brand, findings)
        if llm_findings:
            findings.extend(llm_findings)
            analysis_mode = "ai_assisted"

    # Assign IDs and timestamps
    now = datetime.now(timezone.utc).isoformat()
    for f in findings:
        if "id" not in f:
            f["id"] = f"find-{uuid.uuid4().hex[:8]}"
        if "created_at" not in f:
            f["created_at"] = now

    # Sort findings by severity
    findings.sort(key=lambda x: SEVERITY_ORDER.get(x["severity"], 99))

    run_id = f"run-{uuid.uuid4().hex[:8]}"
    run_data = {
        "id": run_id,
        "content_id": content_id,
        "revision_number": revision_number,
        "analysis_mode": analysis_mode,
        "created_at": now
    }

    # Save to database
    db.save_review_run(run_data, findings)

    return {
        "id": run_id,
        "content_id": content_id,
        "revision_number": revision_number,
        "analysis_mode": analysis_mode,
        "created_at": now,
        "findings_count": len(findings),
        "critical_count": sum(1 for f in findings if f["severity"] == "critical"),
        "high_count": sum(1 for f in findings if f["severity"] == "high"),
        "medium_count": sum(1 for f in findings if f["severity"] == "medium"),
        "low_count": sum(1 for f in findings if f["severity"] == "low"),
        "informational_count": sum(1 for f in findings if f["severity"] == "informational"),
        "findings": findings
    }
