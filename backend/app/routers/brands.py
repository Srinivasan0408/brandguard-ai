from fastapi import APIRouter, HTTPException
from typing import List
from ..db.database import db
from ..models.schemas import Brand, BrandUpdate

router = APIRouter(prefix="/api/brands", tags=["Brand Guidelines"])

@router.get("", response_model=List[Brand])
def list_brands():
    return db.list_brands()

@router.get("/{brand_id}", response_model=Brand)
def get_brand(brand_id: str):
    brand = db.get_brand(brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand

@router.put("/{brand_id}", response_model=Brand)
def update_brand(brand_id: str, updates: BrandUpdate):
    updated = db.update_brand(brand_id, updates.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Brand not found")
    return updated
