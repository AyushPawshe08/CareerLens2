"""
LangGraph state definition.

This is the single object passed between every node in the graph
(START -> preprocess -> resume_analysis -> interview_questions -> END).
Each node reads what it needs and returns a partial dict of updates;
LangGraph merges those into this state.
"""

from __future__ import annotations

from typing import List, Optional, TypedDict

from schemas import InterviewQuestions, ResumeAnalysis


class GraphState(TypedDict, total=False):
    # -------------------------------------------------------------
    # Raw inputs (set before the graph starts)
    # -------------------------------------------------------------
    resume_bytes: bytes           # raw uploaded PDF bytes
    job_description: str          # raw JD text, as submitted by the user

    # -------------------------------------------------------------
    # Preprocess node output
    # -------------------------------------------------------------
    resume_text: str              # extracted + truncated resume text
    jd_text: str                  # cleaned + truncated JD text
    preprocess_ok: bool           # False if extraction failed (e.g. scanned PDF)

    # -------------------------------------------------------------
    # Resume Analysis Agent output
    # -------------------------------------------------------------
    resume_analysis: Optional[ResumeAnalysis]

    # -------------------------------------------------------------
    # Interview Question Agent output
    # -------------------------------------------------------------
    interview_questions: Optional[InterviewQuestions]

    # -------------------------------------------------------------
    # Bookkeeping — surfaced to the client, never silently swallowed
    # -------------------------------------------------------------
    errors: List[str]             # human-readable, non-fatal issues collected along the way
    used_llm_provider: Optional[str]  # which provider actually served the request (debug/telemetry)


def initial_state(resume_bytes: bytes, job_description: str) -> GraphState:
    """Build the starting state for a single run of the graph."""
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