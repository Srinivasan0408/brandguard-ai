import re
from typing import List, Dict, Any

def normalize_price(val: str) -> str:
    # Extracts pure digits e.g. "₹4,999" -> "4999"
    digits = re.sub(r"[^\d]", "", val)
    return digits

def check_approved_facts(content: str, facts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    findings = []

    for fact in facts:
        if fact.get("status") != "active":
            continue

        product_name = fact.get("product_name", "")
        attribute = fact.get("attribute", "")
        approved_val = fact.get("approved_value", "")
        source_title = fact.get("source_title", "Official Brand Factsheet")
        source_url = fact.get("source_url")

        # 1. Price Check
        if attribute.lower() == "price":
            approved_digits = normalize_price(approved_val)
            # Find any currency mention e.g. ₹5,999, ₹ 5,999, Rs 5,999, Rs. 5999, INR 5,999
            price_regex = r"(?:₹|Rs\.?|INR)\s*([0-9]{1,3}(?:,[0-9]{3})*|[0-9]+)"
            matches = list(re.finditer(price_regex, content, re.IGNORECASE))

            for m in matches:
                detected_raw = m.group(0).strip()
                detected_digits = normalize_price(m.group(1))

                # If detected price does not match approved price
                if detected_digits and detected_digits != approved_digits:
                    findings.append({
                        "category": "facts",
                        "severity": "critical",
                        "title": f"Approved Fact Contradiction: {product_name} {attribute}",
                        "excerpt": detected_raw,
                        "explanation": (
                            f"Detected price '{detected_raw}' directly contradicts the approved {attribute} "
                            f"of '{approved_val}' for {product_name}. Publishing unverified or inaccurate pricing "
                            f"exposes the organization to legal, regulatory, and customer trust liabilities."
                        ),
                        "applicable_guideline": f"Verified Product Registry: {product_name} {attribute} must be {approved_val}",
                        "approved_source": f"{source_title} ({source_url})" if source_url else source_title,
                        "recommended_correction": approved_val,
                        "detection_method": "approved_fact_check",
                        "confidence": "high",
                        "status": "open"
                    })

        # 2. Warranty Check
        elif attribute.lower() == "warranty":
            # Check for patterns like "X months warranty", "X year warranty"
            warranty_regex = r"(\b\d+\s*(?:month|months|year|years)\b)\s*(?:hardware\s*)?warranty"
            matches = list(re.finditer(warranty_regex, content, re.IGNORECASE))
            for m in matches:
                detected_raw = m.group(0)
                detected_duration = m.group(1).lower().strip()
                # If it doesn't match approved (e.g. "12 months" or "1 year" vs "6 months")
                approved_norm = approved_val.lower().strip()
                # Equate 1 year and 12 months
                is_match = (
                    detected_duration == approved_norm or
                    (approved_norm == "12 months" and detected_duration in ["1 year", "one year", "12 months"])
                )
                if not is_match:
                    findings.append({
                        "category": "facts",
                        "severity": "high",
                        "title": f"Warranty Specification Mismatch for {product_name}",
                        "excerpt": detected_raw,
                        "explanation": (
                            f"Content mentions warranty as '{detected_raw}', but approved specification is "
                            f"'{approved_val}' according to standard enterprise legal agreements."
                        ),
                        "applicable_guideline": f"Approved Warranty: {approved_val}",
                        "approved_source": source_title,
                        "recommended_correction": f"{approved_val} warranty",
                        "detection_method": "approved_fact_check",
                        "confidence": "high",
                        "status": "open"
                    })

    return findings
