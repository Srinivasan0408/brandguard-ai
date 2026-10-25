import re
from typing import List, Dict, Any

def check_required_elements(content: str, brand: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    required_phrases = brand.get("required_phrases", [])

    for phrase in required_phrases:
        # Check if phrase is contained (case-insensitive)
        if phrase.lower() not in content.lower():
            findings.append({
                "category": "requirements",
                "severity": "low",
                "title": f"Missing Mandatory Disclaimer / Phrase: '{phrase}'",
                "excerpt": "[Omitted from submitted copy]",
                "explanation": (
                    f"Brand compliance requires the standard phrase or disclaimer: '{phrase}' "
                    f"on formal marketing publications for {brand.get('name', 'the brand')}."
                ),
                "applicable_guideline": f"Mandatory Disclosure: Include '{phrase}' in published copy",
                "approved_source": "Brand Knowledge Hub - Compliance Disclosures",
                "recommended_correction": f"\n\n{phrase}",
                "detection_method": "deterministic_rule",
                "confidence": "high",
                "status": "open"
            })

    return findings
