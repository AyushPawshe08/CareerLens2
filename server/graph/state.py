from __future__ import annotations

from typing import List, Optional, TypedDict

from models.schemas import InterviewQuestions, ResumeAnalysis


class GraphState(TypedDict, total=False):
    resume_bytes: bytes
    job_description: str
    resume_text: str
    jd_text: str
    preprocess_ok: bool
    resume_analysis: Optional[ResumeAnalysis]
    interview_questions: Optional[InterviewQuestions]
    errors: List[str]
    used_llm_provider: Optional[str]


def initial_state(resume_bytes: bytes, job_description: str) -> GraphState:
    return GraphState(
        resume_bytes=resume_bytes,
        job_description=job_description,
        resume_text="",
        jd_text="",
        preprocess_ok=False,
        resume_analysis=None,
        interview_questions=None,
        errors=[],
        used_llm_provider=None,
    )