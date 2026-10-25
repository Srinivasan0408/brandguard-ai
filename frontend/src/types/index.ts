export type ContentStatus = 'draft' | 'in_review' | 'changes_requested' | 'approved' | 'rejected';

export type SeverityLevel = 'critical' | 'high' | 'medium' | 'low' | 'informational';

export type CategoryType = 'terminology' | 'facts' | 'claims' | 'tone' | 'accessibility' | 'requirements';

export type FindingStatus = 'open' | 'applied' | 'dismissed' | 'manual_edited';

export interface Finding {
  id: string;
  review_run_id: string;
  category: CategoryType;
  severity: SeverityLevel;
  title: string;
  excerpt: string;
  explanation: string;
  applicable_guideline: string;
  approved_source?: string;
  recommended_correction: string;
  detection_method: string;
  confidence: string;
  status: FindingStatus;
  dismissal_reason?: string;
  created_at: string;
}

export interface ReviewRun {
  id: string;
  content_id: string;
  revision_number: number;
  analysis_mode: 'deterministic' | 'ai_assisted';
  created_at: string;
  findings_count: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  informational_count: number;
  findings: Finding[];
}

export interface ContentRevision {
  id: string;
  content_id: string;
  revision_number: number;
  content_text: string;
  image_alt_text?: string;
  created_by: string;
  created_at: string;
  change_summary?: string;
}

export interface ReviewComment {
  id: string;
  content_id: string;
  revision_number: number;
  author_name: string;
  author_role: string;
  comment_text: string;
  created_at: string;
}

export interface ApprovalEvent {
  id: string;
  content_id: string;
  revision_number: number;
  event_type: string;
  actor_name: string;
  actor_role: string;
  comments?: string;
  created_at: string;
}

export interface ContentItem {
  id: string;
  brand_id: string;
  title: string;
  content_type: string;
  channel: string;
  raw_content: string;
  image_alt_text?: string;
  campaign_ref?: string;
  status: ContentStatus;
  current_revision: number;
  created_by: string;
  reviewer_id?: string;
  created_at: string;
  updated_at: string;
  latest_review?: ReviewRun;
  revisions: ContentRevision[];
  comments: ReviewComment[];
  approval_history: ApprovalEvent[];
}

export interface Brand {
  id: string;
  name: string;
  description: string;
  preferred_tone: string;
  target_audience: string;
  approved_terminology: string[];
  prohibited_terminology: string[];
  required_phrases: string[];
  style_guidelines: string[];
  formatting_preferences: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface ApprovedFact {
  id: string;
  brand_id: string;
  product_name: string;
  attribute: string;
  approved_value: string;
  unit_or_currency?: string;
  source_title: string;
  source_url?: string;
  verification_date: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface CategoryMetric {
  category: string;
  count: number;
  percentage: number;
}

export interface SeverityMetric {
  severity: string;
  count: number;
}

export interface CommonMistake {
  issue: string;
  category: string;
  count: number;
  recommendation: string;
}

export interface GovernanceInsights {
  total_reviews_run: number;
  total_content_items: number;
  pending_approval_count: number;
  approved_count: number;
  changes_requested_count: number;
  total_findings_detected: number;
  category_distribution: CategoryMetric[];
  severity_distribution: SeverityMetric[];
  frequent_mistakes: CommonMistake[];
  rule_clarification_suggestions: string[];
  has_sufficient_data: boolean;
}

export interface HealthStatus {
  status: string;
  app_name: string;
  version: string;
  environment: string;
  demo_mode: boolean;
  database: {
    type: string;
    connected: boolean;
    brands_loaded: number;
  };
  review_engine: {
    analysis_mode: string;
    llm_configured: boolean;
    llm_provider: string;
  };
}
