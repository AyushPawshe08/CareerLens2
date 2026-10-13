from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import get_db
from api.dependencies import get_current_user
from graph.build import compiled_graph
from graph.state import initial_state
from models.db_models import AnalysisHistory, User
from models.schemas import AnalyzeResponse

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    resume: UploadFile = File(..., description="Resume as a PDF, max 2 pages."),
    job_description: str = Form(..., min_length=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnalyzeResponse:
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

    state = initial_state(resume_bytes=resume_bytes, job_description=job_description)
    result = await compiled_graph.ainvoke(state)

    if result.get("resume_analysis") is None:
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
    from models.schemas import InterviewQuestions

    return InterviewQuestions()