"""
FastAPI application entrypoint.

Run with:  uvicorn app.main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth_routes import router as auth_router
from history_routes import router as history_router
from routes import router as analyze_router
from config import settings

app = FastAPI(
    title=settings.app_name,
    description="AI Resume Analyzer and Interview Preparation Platform",
    version="2.0.0",
    debug=settings.debug,
)

# NOTE: tighten allow_origins to your actual frontend domain(s) before
# deploying to production — "*" is fine for local dev only.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(history_router)
app.include_router(analyze_router)


@app.on_event("startup")
async def on_startup() -> None:
    # Creates missing tables only — does not migrate existing ones.
    # See app/core/database.py docstring: switch to Alembic once the
    # schema stabilizes.
    from database import init_db

    await init_db()


@app.get("/health", tags=["meta"])
async def health() -> dict:
    """Basic liveness check — does NOT verify LLM provider connectivity.
    Extend this later with a lightweight provider ping if you want
    readiness-style health checks."""
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}