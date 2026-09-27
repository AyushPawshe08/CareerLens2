"""
SQLAlchemy ORM models (database tables).

Keep these separate from app/models/schemas.py (Pydantic models used for
LLM structured output / API request-response shapes) — ORM models and
API/LLM schemas are different concerns and will drift apart over time.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    analyses: Mapped[list["AnalysisHistory"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug convenience only
        return f"<User id={self.id} email={self.email}>"


class AnalysisHistory(Base):
    """One row per resume+JD analysis run. Stores extracted TEXT only —
    never the raw PDF bytes (see build discussion: PII/storage cost
    trade-off). Populated once the API layer is wired to persist results
    (later file) — this is just the table definition for now.
    """

    __tablename__ = "analysis_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    resume_text: Mapped[str] = mapped_column(Text, nullable=False)
    job_description: Mapped[str] = mapped_column(Text, nullable=False)

    # Stored as JSON text for now (simplest to wire up); if querying inside
    # these blobs becomes a need later (e.g. "find all analyses mentioning
    # Docker"), migrate this column to native JSONB instead.
    resume_analysis_json: Mapped[str] = mapped_column(Text, nullable=False)
    interview_questions_json: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped["User"] = relationship(back_populates="analyses")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AnalysisHistory id={self.id} user_id={self.user_id}>"