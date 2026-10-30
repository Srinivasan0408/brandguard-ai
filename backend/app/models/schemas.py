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

# --- Organizations ---
class Organization(BaseModel):
    id: str
    name: str
    slug: str
    created_at: str

# --- Users & Auth ---
class UserRole(str, Enum):
    ADMIN = "admin"
    REVIEWER = "reviewer"
    CREATOR = "creator"

class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    role: UserRole
    organization_id: str

class User(UserBase):
    id: str
    created_at: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

# --- Visual Asset Analysis ---
class VisualCheckResult(BaseModel):
    check_name: str
    status: str # "pass", "fail", "warning", "needs_review"
    severity: SeverityLevel
    observed_value: str
    expected_value: str
    explanation: str
    recommended_fix: str
    uncertainty_note: Optional[str] = None

class DominantColor(BaseModel):
    hex: str
    rgb: List[int]
    percentage: float
    is_brand_match: bool
    nearest_brand_color: Optional[str] = None

class VisualFinding(BaseModel):
    category: str
    severity: SeverityLevel
    title: str
    trigger_text: str
    applicable_guideline: str
    recommended_correction: str
    explanation: str
    confidence: str

class VisualAnalysisResponse(BaseModel):
    file_name: str
    file_size_bytes: int
    dimensions: Dict[str, int]
    format: str
    dominant_colors: List[DominantColor]
    brand_palette: List[str]
    palette_compliance_score: float
    contrast_ratio: Optional[float] = None
    wcag_aa_compliant: Optional[bool] = None
    checks: List[VisualCheckResult]
    analyzed_at: str
    extracted_text: Optional[str] = None
    ocr_available: bool = False
    ocr_confidence: Optional[float] = None
    ocr_status_note: Optional[str] = None
    ocr_findings: List[VisualFinding] = []


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
    organization_id: Optional[str] = "org-novatech"

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
    organization_id: Optional[str] = "org-novatech"

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
    evidence_record_id: Optional[str] = None
    evidence_status: Optional[str] = "verified" # "verified", "unverified", "insufficient_evidence", "advisory"
    recommended_correction: str
    correction_rationale: Optional[str] = None
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
    organization_id: Optional[str] = "org-novatech"
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
    organization_id: Optional[str] = "org-novatech"
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
