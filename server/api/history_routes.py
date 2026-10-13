from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from api.dependencies import get_current_user
from models.db_models import AnalysisHistory, User
from models.history_schema import (
    HistoryItem,
    HistoryListItem,
    InterviewQuestions,
    ResumeAnalysis,
)

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=list[HistoryListItem])
async def list_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 20,
    offset: int = 0,
) -> list[HistoryListItem]:
    limit = max(1, min(limit, 100))

    stmt = (
        select(AnalysisHistory)
        .where(AnalysisHistory.user_id == current_user.id)
        .order_by(desc(AnalysisHistory.created_at))
        .limit(limit)
        .offset(offset)
    )
    rows = (await db.scalars(stmt)).all()

    items = []
    for row in rows:
        try:
            analysis = ResumeAnalysis.model_validate_json(row.resume_analysis_json)
        except Exception:
            continue
        items.append(
            HistoryListItem(
                id=str(row.id),
                created_at=row.created_at.isoformat(),
                summary=analysis.summary,
                match_score=analysis.match_score,
            )
        )
    return items


@router.get("/{history_id}", response_model=HistoryItem)
async def get_history_item(
    history_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HistoryItem:
    not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="History item not found."
    )

    try:
        history_uuid = uuid.UUID(history_id)
    except ValueError:
        raise not_found

    row = await db.get(AnalysisHistory, history_uuid)

    if row is None or row.user_id != current_user.id:
        raise not_found

    try:
        resume_analysis = ResumeAnalysis.model_validate_json(row.resume_analysis_json)
        interview_questions = (
            InterviewQuestions.model_validate_json(row.interview_questions_json)
            if row.interview_questions_json
            else InterviewQuestions()
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stored analysis data is corrupted and could not be read.",
        ) from exc

    return HistoryItem(
        id=str(row.id),
        created_at=row.created_at.isoformat(),
        job_description=row.job_description,
        resume_text=row.resume_text,
        resume_analysis=resume_analysis,
        interview_questions=interview_questions,
    )