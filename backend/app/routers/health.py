from fastapi import APIRouter
from ..config import settings
from ..db.database import db
from ..engine.llm_helper import llm_helper

router = APIRouter(tags=["Health & Status"])

@router.get("/health")
def get_health():
    brands = db.list_brands()
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "demo_mode": settings.DEMO_MODE,
        "database": {
            "type": "supabase" if settings.has_supabase else "sqlite_local",
            "connected": True,
            "brands_loaded": len(brands)
        },
        "review_engine": {
            "analysis_mode": "ai_assisted" if llm_helper.is_available() else "deterministic_rule_engine",
            "llm_configured": llm_helper.is_available(),
            "llm_provider": settings.LLM_PROVIDER if llm_helper.is_available() else "none"
        }
    }
