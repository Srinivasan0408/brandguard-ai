import uuid
from datetime import datetime, timezone

NOVATECH_BRAND_ID = "brand-novatech-001"

SAMPLE_BRAND = {
    "id": NOVATECH_BRAND_ID,
    "name": "NovaTech",
    "description": "Enterprise cloud security, intelligent infrastructure, and next-generation AI hardware solutions.",
    "preferred_tone": "Professional, clear, helpful, and trustworthy. We speak with authoritative calm, avoiding hype and hyperbole.",
    "target_audience": "Enterprise IT leaders, CISOs, DevOps teams, and tech-forward business executives.",
    "approved_terminology": [
        "NovaTech Pro",
        "NovaTech AI Suite",
        "QuantumSync",
        "ZeroTrust Cloud",
        "CyberShield Core"
    ],
    "prohibited_terminology": [
        "cheap",
        "unbreakable",
        "foolproof",
        "magic solution",
        "hack-proof",
        "100% secure",
        "rock-bottom price"
    ],
    "required_phrases": [
        "Enterprise security powered by NovaTech",
        "Terms & conditions apply"
    ],
    "style_guidelines": [
        "Avoid exaggerated or misleading promotional claims.",
        "Use simple, accessible language without unnecessary jargon.",
        "Do not promise guaranteed results or 100% efficacy without verified third-party empirical evidence.",
        "Always use the approved product name 'NovaTech Pro' consistently; avoid abbreviations like 'N-Pro' or 'Nova Pro'.",
        "Use the configured currency and pricing information (₹4,999 for NovaTech Pro).",
        "Do not invent unverified product capabilities or speculate on unreleased roadmaps.",
        "Ensure all promotional images include descriptive alternative text for accessibility."
    ],
    "formatting_preferences": {
        "price_format": "₹{amount}",
        "date_format": "YYYY-MM-DD",
        "disclaimer_position": "footer"
    },
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-01T00:00:00Z"
}

SAMPLE_FACTS = [
    {
        "id": "fact-novatech-001",
        "brand_id": NOVATECH_BRAND_ID,
        "product_name": "NovaTech Pro",
        "attribute": "Price",
        "approved_value": "₹4,999",
        "unit_or_currency": "INR (₹)",
        "source_title": "NovaTech Official Q4 Product Catalog & Pricing Matrix",
        "source_url": "https://novatech.internal/catalog/2026-pricing",
        "verification_date": "2026-01-15",
        "status": "active",
        "created_at": "2026-01-15T10:00:00Z",
        "updated_at": "2026-01-15T10:00:00Z"
    },
    {
        "id": "fact-novatech-002",
        "brand_id": NOVATECH_BRAND_ID,
        "product_name": "NovaTech Pro",
        "attribute": "Warranty",
        "approved_value": "12 months",
        "unit_or_currency": "Months",
        "source_title": "NovaTech Standard Hardware Warranty Agreement",
        "source_url": "https://novatech.internal/legal/warranty",
        "verification_date": "2026-01-10",
        "status": "active",
        "created_at": "2026-01-10T10:00:00Z",
        "updated_at": "2026-01-10T10:00:00Z"
    },
    {
        "id": "fact-novatech-003",
        "brand_id": NOVATECH_BRAND_ID,
        "product_name": "NovaTech Pro",
        "attribute": "Battery Life",
        "approved_value": "24 hours",
        "unit_or_currency": "Hours",
        "source_title": "NovaTech Lab Benchmark Test Report #NB-204",
        "source_url": "https://novatech.internal/specs/battery",
        "verification_date": "2026-02-01",
        "status": "active",
        "created_at": "2026-02-01T10:00:00Z",
        "updated_at": "2026-02-01T10:00:00Z"
    },
    {
        "id": "fact-novatech-004",
        "brand_id": NOVATECH_BRAND_ID,
        "product_name": "NovaTech AI Suite",
        "attribute": "Deployment Time",
        "approved_value": "under 15 minutes",
        "unit_or_currency": "Minutes",
        "source_title": "Cloud Architecture Whitepaper v3.2",
        "source_url": "https://novatech.internal/whitepapers/deployment",
        "verification_date": "2026-01-20",
        "status": "active",
        "created_at": "2026-01-20T10:00:00Z",
        "updated_at": "2026-01-20T10:00:00Z"
    }
]

SAMPLE_DEMO_POSTS = [
    {
        "id": "demo-content-invalid",
        "title": "High-Risk Promotional Campaign (Contains Violations)",
        "content_type": "social",
        "channel": "LinkedIn & X / Twitter",
        "raw_content": (
            "Get the all-new Nova Pro today for a cheap price of only ₹5,999! "
            "Our revolutionary system provides 100% guaranteed results and unbreakable cyber protection. "
            "The best in the world for enterprise infrastructure, risk-free!"
        ),
        "image_alt_text": "",  # missing alt text
        "campaign_ref": "Q1-LAUNCH-CAMPAIGN",
        "notes": "Deliberately triggers: unapproved product name 'Nova Pro', prohibited words 'cheap' & 'unbreakable', price mismatch (₹5,999 vs ₹4,999), unsupported guarantees ('100% guaranteed results', 'risk-free'), and missing required disclaimer."
    },
    {
        "id": "demo-content-valid",
        "title": "Approved Product Announcement (Compliant)",
        "content_type": "social",
        "channel": "LinkedIn",
        "raw_content": (
            "Introducing the NovaTech Pro, engineered for resilient enterprise infrastructure. "
            "Available now starting at ₹4,999 with a comprehensive 12 months hardware warranty. "
            "Experience proactive zero-trust threat management with seamless deployment.\n\n"
            "Enterprise security powered by NovaTech. Terms & conditions apply."
        ),
        "image_alt_text": "Executive workstation showing the sleek NovaTech Pro hardware unit with security dashboard",
        "campaign_ref": "Q1-ENTERPRISE-ANNOUNCE",
        "notes": "Fully follows all guidelines: exact approved name, correct approved price ₹4,999, warranty 12 months, professional tone, and required phrases included."
    }
]
