from typing import Optional

from pydantic import BaseModel

from models.schemas import InterviewQuestions, ResumeAnalysis


class HistoryItem(BaseModel):
    id: str
    created_at: str
    job_description: str
    resume_text: str
    resume_analysis: ResumeAnalysis
    interview_questions: InterviewQuestions


class HistoryListItem(BaseModel):
    id: str
    created_at: str
    summary: str
    match_score: Optional[int] = None
