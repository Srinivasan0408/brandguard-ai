import re
from typing import List, Dict, Any, Optional

def check_accessibility(content: str, image_alt_text: Optional[str] = None, channel: str = "") -> List[Dict[str, Any]]:
    findings = []

    # 1. Missing Image Alt Text Check
    # If channel or content suggests visual asset usage, or alt text was submitted empty
    if image_alt_text is not None and image_alt_text.strip() == "":
        findings.append({
            "category": "accessibility",
            "severity": "medium",
            "title": "Missing Descriptive Alternative Text (Alt Text)",
            "excerpt": "[Attached Media / Promotional Image]",
            "explanation": (
                "The submitted media item lacks alternative text. Alt text is essential for screen reader users and "
                "helps maintain accessible digital experiences across web and social channels."
            ),
            "applicable_guideline": "Digital Accessibility: All promotional media must include descriptive alt text.",
            "approved_source": "Brand Knowledge Hub - Digital Inclusion Standards",
            "recommended_correction": "Provide a concise 1-2 sentence description detailing the image subject and key visual context.",
            "detection_method": "accessibility_heuristic",
            "confidence": "high",
            "status": "open"
        })
    elif image_alt_text and len(image_alt_text.strip()) < 10:
        findings.append({
            "category": "accessibility",
            "severity": "low",
            "title": "Insufficient Alternative Text Detail",
            "excerpt": image_alt_text,
            "explanation": (
                "The provided alt text is brief or non-descriptive. Meaningful alt text should convey the functional or contextual purpose of the image."
            ),
            "applicable_guideline": "Digital Accessibility: Alt text should be descriptive and meaningful.",
            "approved_source": "Brand Knowledge Hub - Digital Inclusion Standards",
            "recommended_correction": "Expand alt text to describe what is depicted and its relevance to the copy.",
            "detection_method": "accessibility_heuristic",
            "confidence": "medium",
            "status": "open"
        })

    # 2. Raw or unlabelled URLs (e.g. "click here https://..." or bare links)
    bare_urls = list(re.finditer(r"(?:https?://|www\.)[^\s<]+", content))
    click_here_matches = list(re.finditer(r"\b(?:click\s+here|read\s+more|link)\b", content, re.IGNORECASE))
    
    if click_here_matches and bare_urls:
        findings.append({
            "category": "accessibility",
            "severity": "low",
            "title": "Non-Descriptive Link Anchor Text ('click here')",
            "excerpt": click_here_matches[0].group(0),
            "explanation": (
                "Using vague anchor phrases like 'click here' creates navigational ambiguity for assistive technology users. "
                "Links should describe the destination or action clearly (e.g., 'View the NovaTech Pro documentation')."
            ),
            "applicable_guideline": "Accessibility Guidelines: Use descriptive hyperlink descriptions.",
            "approved_source": "Brand Knowledge Hub - Web & Social Usability Standards",
            "recommended_correction": "Replace 'click here' with clear descriptive text indicating the destination page.",
            "detection_method": "accessibility_heuristic",
            "confidence": "high",
            "status": "open"
        })

    return findings
