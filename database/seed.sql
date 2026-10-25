-- ============================================================
-- BRANDGUARD AI: SEED DATA FOR SUPABASE POSTGRESQL
-- Fictional Brand: NovaTech
-- ============================================================

INSERT INTO brands (
    id, name, description, preferred_tone, target_audience,
    approved_terminology, prohibited_terminology, required_phrases,
    style_guidelines, formatting_preferences, created_at, updated_at
) VALUES (
    'brand-novatech-001',
    'NovaTech',
    'Enterprise cloud security, intelligent infrastructure, and next-generation AI hardware solutions.',
    'Professional, clear, helpful, and trustworthy. We speak with authoritative calm, avoiding hype and hyperbole.',
    'Enterprise IT leaders, CISOs, DevOps teams, and tech-forward business executives.',
    '["NovaTech Pro", "NovaTech AI Suite", "QuantumSync", "ZeroTrust Cloud", "CyberShield Core"]'::jsonb,
    '["cheap", "unbreakable", "foolproof", "magic solution", "hack-proof", "100% secure", "rock-bottom price"]'::jsonb,
    '["Enterprise security powered by NovaTech", "Terms & conditions apply"]'::jsonb,
    '["Avoid exaggerated or misleading promotional claims.", "Use simple, accessible language without unnecessary jargon.", "Do not promise guaranteed results or 100% efficacy without verified third-party empirical evidence.", "Always use the approved product name NovaTech Pro consistently; avoid abbreviations like N-Pro or Nova Pro.", "Use the configured currency and pricing information (₹4,999 for NovaTech Pro).", "Do not invent unverified product capabilities or speculate on unreleased roadmaps.", "Ensure all promotional images include descriptive alternative text for accessibility."]'::jsonb,
    '{"price_format": "₹{amount}", "date_format": "YYYY-MM-DD", "disclaimer_position": "footer"}'::jsonb,
    '2026-01-01T00:00:00Z',
    '2026-01-01T00:00:00Z'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO approved_facts (
    id, brand_id, product_name, attribute, approved_value,
    unit_or_currency, source_title, source_url, verification_date, status, created_at, updated_at
) VALUES 
(
    'fact-novatech-001',
    'brand-novatech-001',
    'NovaTech Pro',
    'Price',
    '₹4,999',
    'INR (₹)',
    'NovaTech Official Q4 Product Catalog & Pricing Matrix',
    'https://novatech.internal/catalog/2026-pricing',
    '2026-01-15',
    'active',
    '2026-01-15T10:00:00Z',
    '2026-01-15T10:00:00Z'
),
(
    'fact-novatech-002',
    'brand-novatech-001',
    'NovaTech Pro',
    'Warranty',
    '12 months',
    'Months',
    'NovaTech Standard Hardware Warranty Agreement',
    'https://novatech.internal/legal/warranty',
    '2026-01-10',
    'active',
    '2026-01-10T10:00:00Z',
    '2026-01-10T10:00:00Z'
),
(
    'fact-novatech-003',
    'brand-novatech-001',
    'NovaTech Pro',
    'Battery Life',
    '24 hours',
    'Hours',
    'NovaTech Lab Benchmark Test Report #NB-204',
    'https://novatech.internal/specs/battery',
    '2026-02-01',
    'active',
    '2026-02-01T10:00:00Z',
    '2026-02-01T10:00:00Z'
),
(
    'fact-novatech-004',
    'brand-novatech-001',
    'NovaTech AI Suite',
    'Deployment Time',
    'under 15 minutes',
    'Minutes',
    'Cloud Architecture Whitepaper v3.2',
    'https://novatech.internal/whitepapers/deployment',
    '2026-01-20',
    'active',
    '2026-01-20T10:00:00Z',
    '2026-01-20T10:00:00Z'
) ON CONFLICT (id) DO NOTHING;
