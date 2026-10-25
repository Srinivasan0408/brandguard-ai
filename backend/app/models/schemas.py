from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ContentStatus(str, Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    CHANGES_REQUESTED = "changes_requested"
    APPROVED = "approved"
    REJECTED = "rejected"

class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"

class CategoryType(str, Enum):
    TERMINOLOGY = "terminology"
    FACTS = "facts"
    CLAIMS = "claims"
    TONE = "tone"
    ACCESSIBILITY = "accessibility"
    REQUIREMENTS = "requirements"

class DetectionMethod(str, Enum):
    DETERMINISTIC_RULE = "deterministic_rule"
    APPROVED_FACT_CHECK = "approved_fact_check"
    HEURISTIC_CHECK = "heuristic_check"
    LLM_ASSISTED = "llm_assisted"
    ACCESSIBILITY_HEURISTIC = "accessibility_heuristic"

class FindingStatus(str, Enum):
    OPEN = "open"
    APPLIED = "applied"
    DISMISSED = "dismissed"
    MANUAL_EDITED = "manual_edited"

# --- Brands ---
class BrandBase(BaseModel):
    name: str
    description: str
    preferred_tone: str
    target_audience: str
    approved_terminology: List[str] = []
    prohibited_terminology: List[str] = []
    required_phrases: List[str] = []
    style_guidelines: List[str] = []
    formatting_preferences: Dict[str, Any] = {}

class Brand(BrandBase):
    id: str
    created_at: str
    updated_at: str

class BrandCreate(BrandBase):
    pass

class BrandUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    preferred_tone: Optional[str] = None
    target_audience: Optional[str] = None
    approved_terminology: Optional[List[str]] = None
    prohibited_terminology: Optional[List[str]] = None
    required_phrases: Optional[List[str]] = None
    style_guidelines: Optional[List[str]] = None
    formatting_preferences: Optional[Dict[str, Any]] = None

# --- Approved Facts ---
class ApprovedFactBase(BaseModel):
    brand_id: str
    product_name: str
    attribute: str
    approved_value: str
    unit_or_currency: Optional[str] = None
    source_title: str
    source_url: Optional[str] = None
    verification_date: str
    status: str = "active"

class ApprovedFact(ApprovedFactBase):
    id: str
    created_at: str
    updated_at: str

class ApprovedFactCreate(ApprovedFactBase):
    pass

class ApprovedFactUpdate(BaseModel):
    product_name: Optional[str] = None
    attribute: Optional[str] = None
    approved_value: Optional[str] = None
    unit_or_currency: Optional[str] = None
    source_title: Optional[str] = None
    source_url: Optional[str] = None
    verification_date: Optional[str] = None
    status: Optional[str] = None

# --- Findings ---
class Finding(BaseModel):
    id: str
    review_run_id: str
    category: CategoryType
    severity: SeverityLevel
    title: str
    excerpt: str
    explanation: str
    applicable_guideline: str
    approved_source: Optional[str] = None
    recommended_correction: str
    detection_method: DetectionMethod
    confidence: str = "high"
    status: FindingStatus = FindingStatus.OPEN
    dismissal_reason: Optional[str] = None
    created_at: str

class FindingActionRequest(BaseModel):
    action: str  # "apply", "dismiss", "manual_edit"
    dismissal_reason: Optional[str] = None

# --- Revisions & Content Items ---
class ContentRevision(BaseModel):
    id: str
    content_id: str
    revision_number: int
    content_text: str
    image_alt_text: Optional[str] = None
    created_by: str
    created_at: str
    change_summary: Optional[str] = None

class ReviewRun(BaseModel):
    id: str
    content_id: str
    revision_number: int
    analysis_mode: str  # "deterministic" or "ai_assisted"
    created_at: str
    findings_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    informational_count: int
    findings: List[Finding] = []

class ReviewComment(BaseModel):
    id: str
    content_id: str
    revision_number: int
    author_name: str
    author_role: str  # "creator", "reviewer", "admin"
    comment_text: str
    created_at: str

class ApprovalEvent(BaseModel):
    id: str
    content_id: str
    revision_number: int
    event_type: str  # "submitted", "approved", "changes_requested", "rejected", "revised"
    actor_name: str
    actor_role: str
    comments: Optional[str] = None
    created_at: str

class ContentItem(BaseModel):
    id: str
    brand_id: str
    title: str
    content_type: str  # social, marketing, website, email, ad, document
    channel: str
    raw_content: str
    image_alt_text: Optional[str] = None
    campaign_ref: Optional[str] = None
    status: ContentStatus
    current_revision: int
    created_by: str
    reviewer_id: Optional[str] = None
    created_at: str
    updated_at: str
    latest_review: Optional[ReviewRun] = None
    revisions: List[ContentRevision] = []
    comments: List[ReviewComment] = []
    approval_history: List[ApprovalEvent] = []

class ContentCreateRequest(BaseModel):
    brand_id: str
    title: str
    content_type: str
    channel: str
    raw_content: str
    image_alt_text: Optional[str] = None
    campaign_ref: Optional[str] = None
    created_by: str = "Creator (Demo User)"

class ContentReviseRequest(BaseModel):
    content_text: str
    image_alt_text: Optional[str] = None
    change_summary: str = "Manual edits"
    actor_name: str = "Creator (Demo User)"
    actor_role: str = "creator"

class ContentWorkflowAction(BaseModel):
    actor_name: str
    actor_role: str  # creator, reviewer, admin
    comments: Optional[str] = None

# --- Governance Insights ---
class CategoryMetric(BaseModel):
    category: str
    count: int
    percentage: float

class SeverityMetric(BaseModel):
    severity: str
    count: int

class CommonMistake(BaseModel):
    issue: str
    category: str
    count: int
    recommendation: str

class GovernanceInsights(BaseModel):
    total_reviews_run: int
    total_content_items: int
    pending_approval_count: int
    approved_count: int
    changes_requested_count: int
    total_findings_detected: int
    category_distribution: List[CategoryMetric]
    severity_distribution: List[SeverityMetric]
    frequent_mistakes: List[CommonMistake]
    rule_clarification_suggestions: List[str]
    has_sufficient_data: bool
