"""
Core Pydantic models for CareerLens.

These are the structured-output contracts the LLM must fill in, and the
shapes every downstream component (API responses, LangGraph state) relies on.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Resume Analysis
# ---------------------------------------------------------------------------

class ResumeAnalysis(BaseModel):
    """Structured output of the Resume Analysis Agent."""

    summary: str = Field(
        ..., description="2-4 sentence summary of the candidate's profile relative to the JD."
    )
    matched_skills: List[str] = Field(
        default_factory=list,
        description="Skills present in both the resume and the job description.",
    )
    missing_skills: List[str] = Field(
        default_factory=list,
        description="Skills required by the JD but not found in the resume.",
    )
    suggested_roles: List[str] = Field(
        default_factory=list,
        description="Job titles/roles this resume is a strong fit for.",
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Concrete, actionable suggestions to improve the resume for this JD.",
    )
    match_score: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Overall resume-to-JD fit score, 0-100. Optional so older prompts still validate.",
    )


# ---------------------------------------------------------------------------
# Interview Questions
# ---------------------------------------------------------------------------

class QuestionDifficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class InterviewQuestion(BaseModel):
    question: str
    difficulty: QuestionDifficulty = QuestionDifficulty.medium
    why_asked: Optional[str] = Field(
        default=None,
        description="One line on why this question is relevant, tied to the resume/JD.",
    )


class InterviewQuestions(BaseModel):
    """Structured output of the Interview Question Agent.

    NOTE: generated as a single LLM call (not 3 parallel calls) to save
    tokens/latency — see build notes.
    """

    technical: List[InterviewQuestion] = Field(default_factory=list)
    hr: List[InterviewQuestion] = Field(default_factory=list)
    behavioral: List[InterviewQuestion] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Top-level request/response models (used by the API layer later)
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    job_description: str = Field(..., min_length=20)
    # resume file itself comes in as an UploadFile in the FastAPI route,
    # not as part of this JSON body.


class AnalyzeResponse(BaseModel):
    resume_analysis: ResumeAnalysis
    interview_questions: InterviewQuestions
    errors: List[str] = Field(default_factory=list)