import re
from typing import List, Dict, Any

TERM_REPLACEMENTS = {
    "cheap": "cost-effective",
    "unbreakable": "highly resilient",
    "foolproof": "user-friendly and robust",
    "magic solution": "comprehensive solution",
    "hack-proof": "enterprise-grade zero-trust security",
    "100% secure": "multi-layered security",
    "rock-bottom price": "competitive enterprise pricing",
    "nova pro": "NovaTech Pro",
    "nova-pro": "NovaTech Pro",
    "n-pro": "NovaTech Pro",
}

def check_terminology(content: str, brand: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    prohibited = brand.get("prohibited_terminology", [])
    approved = brand.get("approved_terminology", [])

    # Check for prohibited terms
    for term in prohibited:
        # Use regex word boundaries
        pattern = r"\b" + re.escape(term) + r"\b"
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        for m in matches:
            matched_text = m.group(0)
            replacement = TERM_REPLACEMENTS.get(term.lower(), "appropriate enterprise terminology")
            findings.append({
                "category": "terminology",
                "severity": "high",
                "title": f"Prohibited Term Detected: '{matched_text}'",
                "excerpt": matched_text,
                "explanation": (
                    f"The term '{matched_text}' is explicitly marked as prohibited in the {brand.get('name', 'brand')} "
                    f"governance guidelines. Using informal or unsubstantiated terms can compromise enterprise credibility."
                ),
                "applicable_guideline": f"Prohibited Terminology: '{term}'",
                "approved_source": "Brand Knowledge Hub - Approved Terminology Register",
                "evidence_record_id": f"guideline-term-{term.lower()}",
                "evidence_status": "verified",
                "recommended_correction": replacement,
                "correction_rationale": f"Replaces prohibited buzzword '{matched_text}' with corporate style approved phrasing '{replacement}'.",
                "detection_method": "deterministic_rule",
                "confidence": "high",
                "status": "open"
            })

    # Check for common brand name inconsistencies
    # E.g. If brand has "NovaTech Pro", flag "Nova Pro" or "N-Pro"
    if "NovaTech Pro" in approved:
        inconsistent_patterns = [
            (r"\bNova\s+Pro\b", "Nova Pro"),
            (r"\bNova-Pro\b", "Nova-Pro"),
            (r"\bN-Pro\b", "N-Pro"),
            (r"\bNovatech\s+pro\b", "Novatech pro"),  # improper casing if strictly NovaTech Pro
        ]
        for pat, label in inconsistent_patterns:
            matches = list(re.finditer(pat, content))
            for m in matches:
                matched_text = m.group(0)
                if matched_text != "NovaTech Pro":
                    findings.append({
                        "category": "terminology",
                        "severity": "medium",
                        "title": f"Inconsistent Product Name: '{matched_text}'",
                        "excerpt": matched_text,
                        "explanation": (
                            f"Found unapproved variation '{matched_text}'. Brand standards require using the exact "
                            f"registered name 'NovaTech Pro' to preserve brand equity and legal trademark protection."
                        ),
                        "applicable_guideline": "Product Naming Standard: Use 'NovaTech Pro' consistently",
                        "approved_source": "Brand Knowledge Hub - Product Naming Registry",
                        "evidence_record_id": "guideline-naming-novatech-pro",
                        "evidence_status": "verified",
                        "recommended_correction": "NovaTech Pro",
                        "correction_rationale": "Adheres strictly to the registered trademark nomenclature 'NovaTech Pro'.",
                        "detection_method": "deterministic_rule",
                        "confidence": "high",
                        "status": "open"
                    })

    return findings
