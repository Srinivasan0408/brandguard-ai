from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import health, brands, facts, reviews, insights

app = FastAPI(
    title="BrandGuard AI API",
    description=(
        "Enterprise Brand Governance & Pre-Publication Compliance Intelligence Platform.\n\n"
        "Features:\n"
        "- Deterministic & LLM-Assisted Brand Review Engine\n"
        "- Approved Facts & Pricing Verification\n"
        "- Terminology & Trademark Guardrails\n"
        "- Full Creator-to-Reviewer Human-in-the-Loop Approval Workflow\n"
        "- Traceable Revision Snapshots & Audit History\n"
        "- Real-Time Governance Insights & Analytics"
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local dev and deployed frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(brands.router)
app.include_router(facts.router)
app.include_router(reviews.router)
app.include_router(insights.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
