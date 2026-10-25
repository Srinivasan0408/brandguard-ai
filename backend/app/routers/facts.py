from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..db.database import db
from ..models.schemas import ApprovedFact, ApprovedFactCreate, ApprovedFactUpdate

router = APIRouter(prefix="/api/facts", tags=["Approved Facts Registry"])

@router.get("", response_model=List[ApprovedFact])
def list_facts(brand_id: Optional[str] = Query(None)):
    return db.list_facts(brand_id=brand_id)

@router.get("/{fact_id}", response_model=ApprovedFact)
def get_fact(fact_id: str):
    fact = db.get_fact(fact_id)
    if not fact:
        raise HTTPException(status_code=404, detail="Fact not found")
    return fact

@router.post("", response_model=ApprovedFact, status_code=201)
def create_fact(fact: ApprovedFactCreate):
    created = db.create_fact(fact.model_dump())
    return created

@router.put("/{fact_id}", response_model=ApprovedFact)
def update_fact(fact_id: str, updates: ApprovedFactUpdate):
    updated = db.update_fact(fact_id, updates.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Fact not found")
    return updated

@router.delete("/{fact_id}")
def delete_fact(fact_id: str):
    success = db.delete_fact(fact_id)
    if not success:
        raise HTTPException(status_code=404, detail="Fact not found")
    return {"message": "Fact deleted successfully", "id": fact_id}
