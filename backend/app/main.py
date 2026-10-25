from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

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
    redoc_url="/redoc",
)

# Frontend build directory
BASE_DIR = Path(file).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend" / "dist"
INDEX_FILE = FRONTEND_DIR / "index.html"

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(health.router)
app.include_router(brands.router)
app.include_router(facts.router)
app.include_router(reviews.router)
app.include_router(insights.router)

# Serve the frontend homepage
@app.get("/", include_in_schema=False)
def serve_homepage():
    if INDEX_FILE.is_file():
        return FileResponse(INDEX_FILE)

    return {
        "message": "BrandGuard AI API is running",
        "frontend_status": "Frontend build not found",
        "expected_path": str(INDEX_FILE),
    }

# Serve frontend assets and support client-side routing
@app.get("/{full_path:path}", include_in_schema=False)
def serve_frontend_routes(full_path: str):
    # Do not intercept API or documentation requests
    if (
        full_path == "health"
        or full_path.startswith(("api/", "docs", "redoc", "openapi.json"))
    ):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")

    requested_file = (FRONTEND_DIR / full_path).resolve()

    # Only serve files located inside the frontend build directory
    if requested_file.is_relative_to(FRONTEND_DIR.resolve()) and requested_file.is_file():
        return FileResponse(requested_file)

    # Return the SPA entry point for client-side routes
    if INDEX_FILE.is_file():
        return FileResponse(INDEX_FILE)

    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Frontend build not found")

if name == "main":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
