import re
from typing import List, Dict, Any

RISKY_CLAIMS_CONFIG = [
    {
        "pattern": r"\b(?:100%|completely|fully)?\s*(?:guaranteed\s+results|guaranteed\s+success)\b",
        "title": "Unsupported Performance Guarantee",
        "severity": "high",
        "guideline": "Advertising Integrity: Do not promise guaranteed results without empirical third-party proof.",
        "explanation": (
            "Absolute performance guarantees ('guaranteed results') create substantial legal exposure and violate "
            "enterprise brand communication standards unless backed by certified empirical proof."
        ),
        "replacement": "demonstrated results in customer benchmarks"
    },
    {
        "pattern": r"\b100%\s*(?:effective|secure|reliable|uptime|foolproof)\b",
        "title": "Absolute Efficacy Claim (100%)",
        "severity": "high",
        "guideline": "Truth in Advertising: Avoid claiming 100% efficacy or absolute infallibility.",
        "explanation": (
            "Stating '100% effective' or '100% secure' is considered an ungrounded absolute claim in enterprise cybersecurity "
            "and infrastructure, where defense-in-depth is the standard."
        ),
        "replacement": "industry-leading multi-layered efficacy"
    },
    {
        "pattern": r"\brisk-free\b",
        "title": "Unsupported 'Risk-Free' Promotional Claim",
        "severity": "medium",
        "guideline": "Promotional Claims: Risk-free claims must explicitly detail guarantee parameters or trial terms.",
        "explanation": (
            "Describing enterprise software or hardware deployments as 'risk-free' is potentially misleading without "
            "clarifying trial terms or SLA coverage."
        ),
        "replacement": "with seamless enterprise onboarding and pilot evaluation"
    },
    {
        "pattern": r"\bthe\s+best\s+in\s+the\s+world\b",
        "title": "Unsubstantiated Superlative ('The best in the world')",
        "severity": "medium",
        "guideline": "Brand Voice: Ground claims in objective benchmarks rather than unverified hyperbole.",
        "explanation": (
            "Subjective superlatives ('the best in the world') detract from authoritative enterprise positioning and "
            "invite regulatory scrutiny."
        ),
        "replacement": "recognized as a top-tier enterprise solution"
    },
    {
        "pattern": r"\b(?:miracle|revolutionary\s+magic|unrivaled\s+perfection)\b",
        "title": "Hyperbolic Marketing Language",
        "severity": "low",
        "guideline": "Professional Voice: Use measured, technical terminology instead of sensationalist hype.",
        "explanation": (
            "Sensationalist buzzwords weaken enterprise credibility among technical decision makers."
        ),
        "replacement": "modern enterprise-grade technology"
    }
]

def check_promotional_claims(content: str, brand: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings = []
    
    for rule in RISKY_CLAIMS_CONFIG:
        matches = list(re.finditer(rule["pattern"], content, re.IGNORECASE))
        for m in matches:
            excerpt = m.group(0)
            findings.append({
                "category": "claims",
                "severity": rule["severity"],
                "title": rule["title"],
                "excerpt": excerpt,
                "explanation": rule["explanation"],
                "applicable_guideline": rule["guideline"],
                "approved_source": "Brand Knowledge Hub - Claims & Advertising Policy",
                "recommended_correction": rule["replacement"],
                "detection_method": "deterministic_rule",
                "confidence": "high",
                "status": "open"
            })

    return findings
