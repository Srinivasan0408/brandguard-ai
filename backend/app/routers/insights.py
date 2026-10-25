from fastapi import APIRouter, Query
from typing import Optional
from ..db.database import db
from ..models.schemas import GovernanceInsights

router = APIRouter(tags=["Governance Insights & Analytics"])

@router.get("/api/insights", response_model=GovernanceInsights)
def get_governance_insights(brand_id: Optional[str] = Query(None)):
    return db.get_governance_insights(brand_id=brand_id)

@router.post("/api/reset-demo")
def reset_demo_database():
    db.reset_database()
    return {"message": "Demo data reset successfully to NovaTech defaults"}
