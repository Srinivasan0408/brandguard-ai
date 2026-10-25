-- ============================================================
-- BRANDGUARD AI: SUPABASE POSTGRESQL SCHEMA WITH RLS
-- Inkloom AI Hackathon - Round 2: The Build
-- Team: TECHSPARKZ
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Profiles Table (linked to Supabase Auth auth.users)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'creator' CHECK (role IN ('creator', 'reviewer', 'admin')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now())
);

-- 2. Brands Table
CREATE TABLE IF NOT EXISTS brands (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    preferred_tone TEXT NOT NULL,
    target_audience TEXT NOT NULL,
    approved_terminology JSONB NOT NULL DEFAULT '[]'::jsonb,
    prohibited_terminology JSONB NOT NULL DEFAULT '[]'::jsonb,
    required_phrases JSONB NOT NULL DEFAULT '[]'::jsonb,
    style_guidelines JSONB NOT NULL DEFAULT '[]'::jsonb,
    formatting_preferences JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now())
);

-- 3. Brand Members Table (RBAC per brand)
CREATE TABLE IF NOT EXISTS brand_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id TEXT NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('creator', 'reviewer', 'admin')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now()),
    UNIQUE(brand_id, user_id)
);

-- 4. Approved Facts Registry
CREATE TABLE IF NOT EXISTS approved_facts (
    id TEXT PRIMARY KEY,
    brand_id TEXT NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    product_name TEXT NOT NULL,
    attribute TEXT NOT NULL,
    approved_value TEXT NOT NULL,
    unit_or_currency TEXT,
    source_title TEXT NOT NULL,
    source_url TEXT,
    verification_date DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'deprecated', 'under_review')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now())
);
CREATE INDEX IF NOT EXISTS idx_facts_brand ON approved_facts(brand_id);
CREATE INDEX IF NOT EXISTS idx_facts_product_attr ON approved_facts(product_name, attribute);

-- 5. Content Items
CREATE TABLE IF NOT EXISTS content_items (
    id TEXT PRIMARY KEY,
    brand_id TEXT NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content_type TEXT NOT NULL CHECK (content_type IN ('social', 'marketing', 'website', 'email', 'ad', 'document')),
    channel TEXT NOT NULL,
    raw_content TEXT NOT NULL,
    image_alt_text TEXT,
    campaign_ref TEXT,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'in_review', 'changes_requested', 'approved', 'rejected')),
    current_revision INTEGER NOT NULL DEFAULT 1,
    created_by TEXT NOT NULL,
    reviewer_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now())
);
CREATE INDEX IF NOT EXISTS idx_content_brand_status ON content_items(brand_id, status);

-- 6. Content Revisions
CREATE TABLE IF NOT EXISTS content_revisions (
    id TEXT PRIMARY KEY,
    content_id TEXT NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
    revision_number INTEGER NOT NULL,
    content_text TEXT NOT NULL,
    image_alt_text TEXT,
    created_by TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now()),
    change_summary TEXT,
    UNIQUE(content_id, revision_number)
);
CREATE INDEX IF NOT EXISTS idx_revisions_content ON content_revisions(content_id);

-- 7. Review Runs
CREATE TABLE IF NOT EXISTS review_runs (
    id TEXT PRIMARY KEY,
    content_id TEXT NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
    revision_number INTEGER NOT NULL,
    analysis_mode TEXT NOT NULL CHECK (analysis_mode IN ('deterministic', 'ai_assisted')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now()),
    findings_count INTEGER NOT NULL DEFAULT 0,
    critical_count INTEGER NOT NULL DEFAULT 0,
    high_count INTEGER NOT NULL DEFAULT 0,
    medium_count INTEGER NOT NULL DEFAULT 0,
    low_count INTEGER NOT NULL DEFAULT 0,
    informational_count INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_runs_content ON review_runs(content_id);

-- 8. Review Findings
CREATE TABLE IF NOT EXISTS review_findings (
    id TEXT PRIMARY KEY,
    review_run_id TEXT NOT NULL REFERENCES review_runs(id) ON DELETE CASCADE,
    category TEXT NOT NULL CHECK (category IN ('terminology', 'facts', 'claims', 'tone', 'accessibility', 'requirements')),
    severity TEXT NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low', 'informational')),
    title TEXT NOT NULL,
    excerpt TEXT NOT NULL,
    explanation TEXT NOT NULL,
    applicable_guideline TEXT NOT NULL,
    approved_source TEXT,
    recommended_correction TEXT NOT NULL,
    detection_method TEXT NOT NULL,
    confidence TEXT NOT NULL DEFAULT 'high',
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'applied', 'dismissed', 'manual_edited')),
    dismissal_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now())
);
CREATE INDEX IF NOT EXISTS idx_findings_run ON review_findings(review_run_id);
CREATE INDEX IF NOT EXISTS idx_findings_category ON review_findings(category);
CREATE INDEX IF NOT EXISTS idx_findings_severity ON review_findings(severity);

-- 9. Review Comments
CREATE TABLE IF NOT EXISTS review_comments (
    id TEXT PRIMARY KEY,
    content_id TEXT NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
    revision_number INTEGER NOT NULL,
    author_name TEXT NOT NULL,
    author_role TEXT NOT NULL,
    comment_text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now())
);
CREATE INDEX IF NOT EXISTS idx_comments_content ON review_comments(content_id);

-- 10. Approval Events (Audit Trail)
CREATE TABLE IF NOT EXISTS approval_events (
    id TEXT PRIMARY KEY,
    content_id TEXT NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
    revision_number INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    actor_name TEXT NOT NULL,
    actor_role TEXT NOT NULL,
    comments TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now())
);
CREATE INDEX IF NOT EXISTS idx_events_content ON approval_events(content_id);

-- ============================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE brands ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE approved_facts ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_revisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE review_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE review_findings ENABLE ROW LEVEL SECURITY;
ALTER TABLE review_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_events ENABLE ROW LEVEL SECURITY;

-- Read policies: Authenticated users can view their brands and content
CREATE POLICY "Public read for brands" ON brands FOR SELECT USING (true);
CREATE POLICY "Public read for approved facts" ON approved_facts FOR SELECT USING (true);
CREATE POLICY "Public read for content items" ON content_items FOR SELECT USING (true);
CREATE POLICY "Public read for revisions" ON content_revisions FOR SELECT USING (true);
CREATE POLICY "Public read for review runs" ON review_runs FOR SELECT USING (true);
CREATE POLICY "Public read for findings" ON review_findings FOR SELECT USING (true);
CREATE POLICY "Public read for comments" ON review_comments FOR SELECT USING (true);
CREATE POLICY "Public read for audit events" ON approval_events FOR SELECT USING (true);

-- Write policies: Allow service role or authenticated users
CREATE POLICY "Full access to service role" ON content_items FOR ALL USING (auth.role() = 'service_role');
