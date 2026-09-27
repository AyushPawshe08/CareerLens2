from typing import Optional

from pydantic import BaseModel

from schemas import InterviewQuestions, ResumeAnalysis


class HistoryItem(BaseModel):
    """One saved analysis run, as returned by GET /api/history and
    GET /api/history/{id}. Built from an AnalysisHistory ORM row — the
    two JSON text columns get parsed back into their structured shapes
    at the API layer, not stored structured (see db_models.py notes).
    """
 
    id: str
    created_at: str
    job_description: str
    resume_text: str
    resume_analysis: ResumeAnalysis
    interview_questions: InterviewQuestions
 
 
class HistoryListItem(BaseModel):
    """Lightweight shape for the list view — omits the large text fields
    (resume_text, job_description, full question list) so listing many
    entries doesn't ship megabytes of text the UI won't render in a list.
    """
 
    id: str
    created_at: str
    summary: str          # resume_analysis.summary, surfaced for the list preview
    match_score: Optional[int] = None
 