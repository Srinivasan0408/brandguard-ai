from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from ..db.database import db
from ..models.schemas import ApprovedFact, ApprovedFactCreate, ApprovedFactUpdate
from ..auth import get_current_user_optional, validate_org_access

router = APIRouter(prefix="/api/facts", tags=["Approved Facts Registry"])

@router.get("", response_model=List[ApprovedFact])
def list_facts(
    brand_id: Optional[str] = Query(None),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    org_id = current_user.get("organization_id") if current_user else None
    return db.list_facts(brand_id=brand_id, organization_id=org_id)

@router.get("/{fact_id}", response_model=ApprovedFact)
def get_fact(
    fact_id: str,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    fact = db.get_fact(fact_id)
    if not fact:
        raise HTTPException(status_code=404, detail="Fact not found")
    
    if current_user:
        validate_org_access(current_user, fact.get("organization_id", "org-novatech"), "approved facts")
        
    return fact

@router.post("", response_model=ApprovedFact, status_code=201)
def create_fact(
    fact: ApprovedFactCreate,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    fact_dict = fact.model_dump()
    if current_user:
        if current_user.get("role") not in ("admin",):
            raise HTTPException(
                status_code=403,
                detail="Forbidden: Only administrators can create or manage approved brand facts."
            )
        fact_dict["organization_id"] = current_user.get("organization_id", "org-novatech")

    created = db.create_fact(fact_dict)

    if current_user:
        db.record_audit_log(
            user_id=current_user.get("id"),
            username=current_user.get("username", "admin"),
            action="fact_created",
            resource_type="fact",
            resource_id=created["id"],
            details=f"Fact '{created['product_name']} - {created['attribute']}' created.",
            organization_id=fact_dict.get("organization_id", "org-novatech")
        )

    return created

@router.put("/{fact_id}", response_model=ApprovedFact)
def update_fact(
    fact_id: str,
    updates: ApprovedFactUpdate,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    existing = db.get_fact(fact_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Fact not found")

    if current_user:
        validate_org_access(current_user, existing.get("organization_id", "org-novatech"), "approved facts")
        if current_user.get("role") not in ("admin",):
            raise HTTPException(
                status_code=403,
                detail="Forbidden: Only administrators can update approved brand facts."
            )

    updated = db.update_fact(fact_id, updates.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Fact not found")

    if current_user:
        db.record_audit_log(
            user_id=current_user.get("id"),
            username=current_user.get("username", "admin"),
            action="fact_updated",
            resource_type="fact",
            resource_id=fact_id,
            details=f"Fact {fact_id} updated.",
            organization_id=existing.get("organization_id", "org-novatech")
        )

    return updated

@router.delete("/{fact_id}")
def delete_fact(
    fact_id: str,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    existing = db.get_fact(fact_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Fact not found")

    if current_user:
        validate_org_access(current_user, existing.get("organization_id", "org-novatech"), "approved facts")
        if current_user.get("role") not in ("admin",):
            raise HTTPException(
                status_code=403,
                detail="Forbidden: Only administrators can delete approved brand facts."
            )

    success = db.delete_fact(fact_id)
    if not success:
        raise HTTPException(status_code=404, detail="Fact not found")

    if current_user:
        db.record_audit_log(
            user_id=current_user.get("id"),
            username=current_user.get("username", "admin"),
            action="fact_deleted",
            resource_type="fact",
            resource_id=fact_id,
            details=f"Fact {fact_id} deleted.",
            organization_id=existing.get("organization_id", "org-novatech")
        )

    return {"message": "Fact deleted successfully", "id": fact_id}
