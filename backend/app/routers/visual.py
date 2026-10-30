from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from ..models.schemas import VisualAnalysisResponse
from ..engine.visual import analyze_visual_asset
from ..db.database import db
from ..auth import get_current_user_optional

router = APIRouter(prefix="/api/visual", tags=["Visual Brand & Accessibility Analysis"])

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024 # 5 MB

@router.post("/analyze", response_model=VisualAnalysisResponse)
async def analyze_image_endpoint(
    file: UploadFile = File(...),
    brand_id: Optional[str] = Form("brand-novatech-001"),
    alt_text: Optional[str] = Form(None),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    # Validate MIME type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image format '{file.content_type}'. BrandGuard AI supports PNG, JPEG, and WebP."
        )

    # Read and validate size
    image_bytes = await file.read()
    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Image size exceeds maximum limit of {MAX_IMAGE_SIZE_BYTES // (1024 * 1024)}MB."
        )

    # Fetch brand
    brand = db.get_brand(brand_id or "brand-novatech-001")
    if not brand:
        brands = db.list_brands()
        brand = brands[0] if brands else {}

    # Run visual analysis
    try:
        analysis_result = analyze_visual_asset(
            image_bytes=image_bytes,
            file_name=file.filename or "uploaded_asset.png",
            brand=brand,
            alt_text=alt_text
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read or decode image file: {str(e)}"
        )

    now = datetime.now(timezone.utc).isoformat()
    analysis_result["analyzed_at"] = now

    # Persist in DB
    user_id = current_user.get("id") if current_user else "demo-user"
    username = current_user.get("username") if current_user else "guest"
    org_id = current_user.get("organization_id") if current_user else brand.get("organization_id", "org-novatech")
    analysis_result["user_id"] = user_id
    analysis_result["brand_id"] = brand.get("id", "brand-novatech-001")
    analysis_result["organization_id"] = org_id
    
    db.save_visual_analysis(analysis_result)

    # Record Audit Event
    db.record_audit_log(
        user_id=user_id,
        username=username,
        action="visual_analysis_run",
        resource_type="visual_asset",
        details=f"Analyzed {file.filename} (palette score: {analysis_result['palette_compliance_score']}%, contrast: {analysis_result['contrast_ratio']}:1)",
        organization_id=org_id
    )

    return VisualAnalysisResponse(**analysis_result)

@router.get("/history")
def get_visual_history(
    brand_id: Optional[str] = None,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    org_id = current_user.get("organization_id") if current_user else None
    return db.list_visual_analyses(brand_id=brand_id, organization_id=org_id)
