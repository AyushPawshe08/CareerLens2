"""
API routes.

Single endpoint: POST /api/analyze
  - multipart/form-data: resume file (PDF) + job_description (text field)
  - returns AnalyzeResponse (resume_analysis + interview_questions + errors)

This layer's job is narrow: validate the HTTP-level concerns (file type,
size), translate ResumeExtractionError into a clean 4xx, invoke the graph,
and shape the response. It should NOT contain business logic — that all
lives in the graph nodes/services.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from dependencies import get_current_user
from build import compiled_graph
from state import initial_state
from db_models import AnalysisHistory, User
from schemas import AnalyzeResponse

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    resume: UploadFile = File(..., description="Resume as a PDF, max 2 pages."),
    job_description: str = Form(..., min_length=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnalyzeResponse:
    # --- HTTP-level validation (before we touch the graph at all) ---
    if resume.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Resume must be uploaded as a PDF file.",
        )

    resume_bytes = await resume.read()

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(resume_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Resume file exceeds the {settings.max_upload_size_mb}MB limit.",
        )

    if not resume_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded resume file is empty.",
        )

    # --- Run the graph ---
    state = initial_state(resume_bytes=resume_bytes, job_description=job_description)
    result = await compiled_graph.ainvoke(state)

    # --- Shape the response ---
    if result.get("resume_analysis") is None:
        # Preprocessing or the LLM step failed outright. Everything useful
        # is already in result["errors"] (set by the relevant node) —
        # surface it as a 422 rather than a bare empty 200.
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Could not complete resume analysis.",
                "errors": result.get("errors", []),
            },
        )

    response = AnalyzeResponse(
        resume_analysis=result["resume_analysis"],
        interview_questions=result.get("interview_questions")
        or _empty_interview_questions(),
        errors=result.get("errors", []),
    )

    # --- Persist to history (best-effort: a DB hiccup shouldn't fail the
    # whole request when the user already has their analysis in hand) ---
    try:
        history_row = AnalysisHistory(
            user_id=current_user.id,
            resume_text=result.get("resume_text", ""),
            job_description=result.get("jd_text", ""),
            resume_analysis_json=response.resume_analysis.model_dump_json(),
            interview_questions_json=response.interview_questions.model_dump_json(),
        )
        db.add(history_row)
        await db.commit()
    except Exception:
        await db.rollback()
        response.errors.append(
            "Analysis succeeded but could not be saved to your history."
        )

    return response


def _empty_interview_questions():
    from schemas import InterviewQuestions

    return InterviewQuestions()