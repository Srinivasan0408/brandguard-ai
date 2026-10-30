from fastapi import APIRouter, Query, Depends
from typing import Optional
from ..db.database import db
from ..auth import get_current_user_optional
from ..models.schemas import GovernanceInsights

router = APIRouter(tags=["Governance Insights & Analytics"])

@router.get("/api/insights", response_model=GovernanceInsights)
def get_governance_insights(
    brand_id: Optional[str] = Query(None),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    org_id = current_user.get("organization_id") if current_user else None
    return db.get_governance_insights(brand_id=brand_id, organization_id=org_id)

@router.post("/api/reset-demo")
def reset_demo_database():
    db.reset_database()
    return {"message": "Demo data reset successfully to NovaTech defaults"}
