from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from ..db.database import db
from ..models.schemas import Brand, BrandUpdate
from ..auth import get_current_user_optional, validate_org_access

router = APIRouter(prefix="/api/brands", tags=["Brand Guidelines"])

@router.get("", response_model=List[Brand])
def list_brands(current_user: Optional[dict] = Depends(get_current_user_optional)):
    org_id = current_user.get("organization_id") if current_user else None
    return db.list_brands(organization_id=org_id)

@router.get("/{brand_id}", response_model=Brand)
def get_brand(brand_id: str, current_user: Optional[dict] = Depends(get_current_user_optional)):
    brand = db.get_brand(brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    if current_user:
        validate_org_access(current_user, brand.get("organization_id", "org-novatech"), "brand guidelines")
    
    return brand

@router.put("/{brand_id}", response_model=Brand)
def update_brand(
    brand_id: str,
    updates: BrandUpdate,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    brand = db.get_brand(brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    if current_user:
        # Organization check
        validate_org_access(current_user, brand.get("organization_id", "org-novatech"), "brand guidelines")
        # Role check: only admins can update brand guidelines
        if current_user.get("role") not in ("admin",):
            raise HTTPException(
                status_code=403,
                detail="Forbidden: Only administrators can update brand guidelines."
            )

    updated = db.update_brand(brand_id, updates.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    if current_user:
        db.record_audit_log(
            user_id=current_user.get("id"),
            username=current_user.get("username", "admin"),
            action="brand_guidelines_updated",
            resource_type="brand",
            resource_id=brand_id,
            details=f"Brand {brand_id} guidelines updated by {current_user.get('username')}.",
            organization_id=brand.get("organization_id", "org-novatech")
        )

    return updated
