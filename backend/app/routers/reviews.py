from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form, Depends
from typing import List, Optional
import os
from ..db.database import db
from ..models.schemas import (
    ContentItem,
    ContentCreateRequest,
    ContentReviseRequest,
    ContentWorkflowAction,
    FindingActionRequest,
    ReviewRun
)
from ..engine.reviewer import run_review
from ..config import settings
from ..auth import get_current_user_optional, require_role, validate_org_access

router = APIRouter(prefix="/api/reviews", tags=["Content Reviews & Approval Workflow"])

ALLOWED_EXTENSIONS = {".txt", ".md", ".markdown"}

@router.get("", response_model=List[ContentItem])
def list_reviews(
    brand_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    org_id = current_user.get("organization_id") if current_user else None
    return db.list_content_items(brand_id=brand_id, status=status, organization_id=org_id)

@router.post("", response_model=ContentItem, status_code=201)
async def create_and_review_content(
    request: ContentCreateRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    # 1. Create content item in database
    data = request.model_dump()
    if current_user:
        data["organization_id"] = current_user.get("organization_id", "org-novatech")
        data["created_by"] = current_user.get("full_name", current_user.get("username", "Creator"))

    created_item = db.create_content_item(data)
    content_id = created_item["id"]

    # 2. Run initial brand compliance review
    await run_review(
        content_id=content_id,
        content_text=request.raw_content,
        brand_id=request.brand_id,
        image_alt_text=request.image_alt_text,
        channel=request.channel,
        revision_number=1
    )

    # 3. Return full item with latest review
    return db.get_content_item(content_id)

@router.get("/{review_id}", response_model=ContentItem)
def get_review(
    review_id: str,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    item = db.get_content_item(review_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")
    if current_user:
        validate_org_access(current_user, item.get("organization_id", "org-novatech"), "review")
    return item

@router.post("/{review_id}/submit", response_model=ContentItem)
def submit_for_human_review(
    review_id: str,
    action: ContentWorkflowAction,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    item = db.get_content_item(review_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")

    if current_user:
        validate_org_access(current_user, item.get("organization_id", "org-novatech"), "review")

    effective_actor = current_user.get("full_name") if current_user else action.actor_name
    effective_role = current_user.get("role") if current_user else action.actor_role

    updated = db.update_content_status(
        content_id=review_id,
        new_status="in_review",
        actor_name=effective_actor,
        actor_role=effective_role,
        comments=action.comments or "Submitted for human governance review"
    )
    return updated

@router.post("/{review_id}/approve", response_model=ContentItem)
def approve_content_review(
    review_id: str,
    action: ContentWorkflowAction,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    item = db.get_content_item(review_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")

    if current_user:
        validate_org_access(current_user, item.get("organization_id", "org-novatech"), "review")

    # If authenticated via token, enforce role from authenticated token
    effective_role = current_user.get("role") if current_user else action.actor_role
    effective_actor = current_user.get("full_name") if current_user else action.actor_name

    # Security & Role check: Only reviewer or admin can approve
    if effective_role not in ("reviewer", "admin"):
        db.record_audit_log(
            user_id=current_user.get("id") if current_user else None,
            username=current_user.get("username") if current_user else action.actor_name,
            action="unauthorized_approval_attempt",
            resource_type="content_item",
            resource_id=review_id,
            details=f"User with role '{effective_role}' attempted to approve content without authorization.",
            organization_id=item.get("organization_id", "org-novatech")
        )
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Only authorized reviewers or administrators can approve content."
        )

    # Separation of duties: Creator cannot approve their own submission unless admin
    if effective_role == "reviewer" and item.get("created_by") == effective_actor:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Creators cannot approve their own content due to separation of duties enforcement."
        )

    # Workflow state check: Must be in_review or changes_requested to approve
    if item["status"] not in ("in_review", "changes_requested"):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot approve content with current status '{item['status']}'. It must be 'in_review'."
        )

    # Enforce: Open critical violations strictly block approval
    latest_review = item.get("latest_review")
    if latest_review and latest_review.get("findings"):
        critical_open = [
            f for f in latest_review["findings"]
            if f.get("severity") == "critical" and f.get("status") in ("open", "pending", None)
        ]
        if critical_open:
            rule_titles = ", ".join([f.get("title", "Critical violation") for f in critical_open])
            raise HTTPException(
                status_code=400,
                detail=f"Cannot approve content with unresolved critical violations: {rule_titles}. All critical issues must be resolved before publication approval."
            )

    updated = db.update_content_status(
        content_id=review_id,
        new_status="approved",
        actor_name=effective_actor,
        actor_role=effective_role,
        comments=action.comments or "Content approved for publication"
    )

    db.record_audit_log(
        user_id=current_user.get("id") if current_user else None,
        username=current_user.get("username") if current_user else action.actor_name,
        action="content_approved",
        resource_type="content_item",
        resource_id=review_id,
        details=f"Content '{item['title']}' was approved for release.",
        organization_id=item.get("organization_id", "org-novatech")
    )

    return updated

@router.post("/{review_id}/reject", response_model=ContentItem)
def reject_content_review(
    review_id: str,
    action: ContentWorkflowAction,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    item = db.get_content_item(review_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")

    if current_user:
        validate_org_access(current_user, item.get("organization_id", "org-novatech"), "review")

    effective_role = current_user.get("role") if current_user else action.actor_role
    effective_actor = current_user.get("full_name") if current_user else action.actor_name

    # Role check: Only reviewer or admin can reject
    if effective_role not in ("reviewer", "admin"):
        db.record_audit_log(
            user_id=current_user.get("id") if current_user else None,
            username=current_user.get("username") if current_user else action.actor_name,
            action="unauthorized_reject_attempt",
            resource_type="content_item",
            resource_id=review_id,
            details=f"User with role '{effective_role}' attempted to reject content without authorization.",
            organization_id=item.get("organization_id", "org-novatech")
        )
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Only authorized reviewers or administrators can reject content."
        )

    updated = db.update_content_status(
        content_id=review_id,
        new_status="rejected",
        actor_name=effective_actor,
        actor_role=effective_role,
        comments=action.comments or "Content rejected by governance reviewer."
    )

    db.record_audit_log(
        user_id=current_user.get("id") if current_user else None,
        username=current_user.get("username") if current_user else action.actor_name,
        action="content_rejected",
        resource_type="content_item",
        resource_id=review_id,
        details=f"Content '{item['title']}' was rejected. Reason: {action.comments or 'Non-compliant'}",
        organization_id=item.get("organization_id", "org-novatech")
    )

    return updated

@router.post("/{review_id}/request-changes", response_model=ContentItem)
def request_changes(
    review_id: str,
    action: ContentWorkflowAction,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    item = db.get_content_item(review_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")

    if current_user:
        validate_org_access(current_user, item.get("organization_id", "org-novatech"), "review")

    effective_role = current_user.get("role") if current_user else action.actor_role
    effective_actor = current_user.get("full_name") if current_user else action.actor_name

    # Security & Role check
    if effective_role not in ("reviewer", "admin"):
        db.record_audit_log(
            user_id=current_user.get("id") if current_user else None,
            username=current_user.get("username") if current_user else action.actor_name,
            action="unauthorized_change_request_attempt",
            resource_type="content_item",
            resource_id=review_id,
            details=f"User with role '{effective_role}' attempted to request changes without authorization.",
            organization_id=item.get("organization_id", "org-novatech")
        )
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Only authorized reviewers can request changes."
        )

    updated = db.update_content_status(
        content_id=review_id,
        new_status="changes_requested",
        actor_name=effective_actor,
        actor_role=effective_role,
        comments=action.comments or "Changes requested by reviewer"
    )

    db.record_audit_log(
        user_id=current_user.get("id") if current_user else None,
        username=current_user.get("username") if current_user else action.actor_name,
        action="content_changes_requested",
        resource_type="content_item",
        resource_id=review_id,
        details=f"Changes requested for '{item['title']}': {action.comments}",
        organization_id=item.get("organization_id", "org-novatech")
    )

    return updated

@router.post("/{review_id}/revise", response_model=ContentItem)
async def revise_content(
    review_id: str,
    req: ContentReviseRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    item = db.get_content_item(review_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")

    if current_user:
        validate_org_access(current_user, item.get("organization_id", "org-novatech"), "review")

    effective_actor = current_user.get("full_name") if current_user else req.actor_name
    effective_role = current_user.get("role") if current_user else req.actor_role

    # 1. Create new revision snapshot
    revised_item = db.revise_content_item(
        content_id=review_id,
        new_text=req.content_text,
        new_alt_text=req.image_alt_text,
        change_summary=req.change_summary,
        actor_name=effective_actor,
        actor_role=effective_role
    )

    # 2. Rerun review engine for the new revision
    await run_review(
        content_id=review_id,
        content_text=req.content_text,
        brand_id=revised_item["brand_id"],
        image_alt_text=req.image_alt_text,
        channel=revised_item["channel"],
        revision_number=revised_item["current_revision"]
    )

    return db.get_content_item(review_id)

@router.patch("/findings/{finding_id}")
def update_finding(finding_id: str, action_req: FindingActionRequest):
    new_status = {
        "apply": "applied",
        "dismiss": "dismissed",
        "manual_edit": "manual_edited"
    }.get(action_req.action, "open")

    success = db.update_finding_status(
        finding_id=finding_id,
        new_status=new_status,
        dismissal_reason=action_req.dismissal_reason
    )
    if not success:
        raise HTTPException(status_code=404, detail="Finding not found")
    return {"message": "Finding updated", "finding_id": finding_id, "status": new_status}

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):
    # Validate extension
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. BrandGuard AI currently supports .txt, .md, and .markdown documents."
        )

    # Read and validate size
    content_bytes = await file.read()
    if len(content_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_BYTES / (1024*1024):.0f}MB."
        )

    try:
        text_content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File encoding error: Document must be UTF-8 encoded text."
        )

    return {
        "filename": filename,
        "size_bytes": len(content_bytes),
        "content_text": text_content
    }
