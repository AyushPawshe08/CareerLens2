from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ResumeAnalysis(BaseModel):
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
    technical: List[InterviewQuestion] = Field(default_factory=list)
    hr: List[InterviewQuestion] = Field(default_factory=list)
    behavioral: List[InterviewQuestion] = Field(default_factory=list)


class AnalyzeRequest(BaseModel):
    job_description: str = Field(..., min_length=20)


class AnalyzeResponse(BaseModel):
    resume_analysis: ResumeAnalysis
    interview_questions: InterviewQuestions
    errors: List[str] = Field(default_factory=list)