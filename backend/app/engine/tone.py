import re
from typing import List, Dict, Any

def check_tone_heuristics(content: str, brand: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    preferred_tone = brand.get("preferred_tone", "Professional, clear, helpful, and trustworthy.")

    # 1. Multiple exclamation marks
    excl_matches = list(re.finditer(r"!{2,}", content))
    if excl_matches:
        findings.append({
            "category": "tone",
            "severity": "low",
            "title": "Unprofessional Punctuation (Multiple Exclamations)",
            "excerpt": excl_matches[0].group(0),
            "explanation": (
                f"Repeated exclamation marks violate the calm, authoritative tone defined in the brand guidelines: "
                f"'{preferred_tone}'. Enterprise communication should convey confidence without sensationalism."
            ),
            "applicable_guideline": "Tone & Style: Authoritative and composed; avoid hype punctuation.",
            "approved_source": "Brand Knowledge Hub - Style & Tone Guide",
            "recommended_correction": "Use standard periods or a single exclamation mark sparingly.",
            "detection_method": "heuristic_check",
            "confidence": "high",
            "status": "open"
        })

    # 2. Aggressive All-Caps Words (SHOUTING)
    # Match words of 4+ characters in ALL CAPS (excluding known acronyms like AI, CISO, SLA, API, URL, Q1)
    known_acronyms = {"AI", "CISO", "SLA", "API", "URL", "Q1", "Q2", "Q3", "Q4", "B2B", "SaaS", "IT", "INR", "USD"}
    caps_matches = [m.group(0) for m in re.finditer(r"\b[A-Z]{4,}\b", content) if m.group(0) not in known_acronyms]
    if len(caps_matches) >= 2:
        findings.append({
            "category": "tone",
            "severity": "medium",
            "title": "Aggressive Capitalization (Shouting Tone)",
            "excerpt": ", ".join(caps_matches[:3]),
            "explanation": (
                f"Multiple capitalized words ({', '.join(caps_matches[:3])}) project an overly aggressive sales pitch, "
                f"conflicting with NovaTech's guideline of 'speaking with authoritative calm, avoiding hype'."
            ),
            "applicable_guideline": "Tone: Maintain authoritative calm and standard sentence casing.",
            "approved_source": "Brand Knowledge Hub - Style & Tone Guide",
            "recommended_correction": "Convert all-caps words to standard sentence case.",
            "detection_method": "heuristic_check",
            "confidence": "high",
            "status": "open"
        })

    # 3. High-Pressure / Urgency sales triggers
    urgency_patterns = [
        r"\bhurry\b",
        r"\bdon't\s+wait\b",
        r"\blimited\s+time\s+only\b",
        r"\bact\s+fast\b",
        r"\bnow\s+or\s+never\b"
    ]
    for pat in urgency_patterns:
        m = re.search(pat, content, re.IGNORECASE)
        if m:
            findings.append({
                "category": "tone",
                "severity": "low",
                "title": f"High-Pressure Sales Urgency: '{m.group(0)}'",
                "excerpt": m.group(0),
                "explanation": (
                    f"Phrases like '{m.group(0)}' invoke high-pressure consumer marketing tactics rather than "
                    f"value-focused enterprise dialogue."
                ),
                "applicable_guideline": "Brand Voice: Value-led communication without artificial scarcity.",
                "approved_source": "Brand Knowledge Hub - Style & Tone Guide",
                "recommended_correction": "Focus on product capabilities, security architecture, and ROI.",
                "detection_method": "heuristic_check",
                "confidence": "medium",
                "status": "open"
            })
            break

    return findings
