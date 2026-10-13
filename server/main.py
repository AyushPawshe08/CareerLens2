from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth_routes import router as auth_router
from api.history_routes import router as history_router
from api.routes import router as analyze_router
from core.config import settings

app = FastAPI(
    title=settings.app_name,
    description="AI Resume Analyzer and Interview Preparation Platform",
    version="2.0.0",
    debug=settings.debug,
)

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
    from core.database import init_db

    await init_db()


@app.get("/health", tags=["meta"])
async def health() -> dict:
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}