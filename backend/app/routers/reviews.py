from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
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

router = APIRouter(prefix="/api/reviews", tags=["Content Reviews & Approval Workflow"])

ALLOWED_EXTENSIONS = {".txt", ".md", ".markdown"}

@router.get("", response_model=List[ContentItem])
def list_reviews(
    brand_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    return db.list_content_items(brand_id=brand_id, status=status)

@router.post("", response_model=ContentItem, status_code=201)
async def create_and_review_content(request: ContentCreateRequest):
    # 1. Create content item in database
    created_item = db.create_content_item(request.model_dump())
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
def get_review(review_id: str):
    item = db.get_content_item(review_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")
    return item

@router.post("/{review_id}/submit", response_model=ContentItem)
def submit_for_human_review(review_id: str, action: ContentWorkflowAction):
    item = db.get_content_item(review_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")

    updated = db.update_content_status(
        content_id=review_id,
        new_status="in_review",
        actor_name=action.actor_name,
        actor_role=action.actor_role,
        comments=action.comments or "Submitted for human governance review"
    )
    return updated

@router.post("/{review_id}/approve", response_model=ContentItem)
def approve_content_review(review_id: str, action: ContentWorkflowAction):
    item = db.get_content_item(review_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")

    # Security & Role check: Only reviewer or admin can approve
    if action.actor_role not in ("reviewer", "admin"):
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Only authorized reviewers or administrators can approve content."
        )

    # Workflow state check: Must be in_review or changes_requested to approve
    if item["status"] not in ("in_review", "changes_requested"):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot approve content with current status '{item['status']}'. It must be 'in_review'."
        )

    updated = db.update_content_status(
        content_id=review_id,
        new_status="approved",
        actor_name=action.actor_name,
        actor_role=action.actor_role,
        comments=action.comments or "Content approved for publication"
    )
    return updated

@router.post("/{review_id}/request-changes", response_model=ContentItem)
def request_changes(review_id: str, action: ContentWorkflowAction):
    item = db.get_content_item(review_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")

    # Security & Role check
    if action.actor_role not in ("reviewer", "admin"):
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Only authorized reviewers can request changes."
        )

    updated = db.update_content_status(
        content_id=review_id,
        new_status="changes_requested",
        actor_name=action.actor_name,
        actor_role=action.actor_role,
        comments=action.comments or "Changes requested by reviewer"
    )
    return updated

@router.post("/{review_id}/revise", response_model=ContentItem)
async def revise_content(review_id: str, req: ContentReviseRequest):
    item = db.get_content_item(review_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")

    # 1. Create new revision snapshot
    revised_item = db.revise_content_item(
        content_id=review_id,
        new_text=req.content_text,
        new_alt_text=req.image_alt_text,
        change_summary=req.change_summary,
        actor_name=req.actor_name,
        actor_role=req.actor_role
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
