"""
Preprocess node — the first step in the LangGraph pipeline
(START -> preprocess -> resume_analysis -> interview_questions -> END).

Responsible for turning raw inputs (resume_bytes, job_description) into
clean, LLM-ready text (resume_text, jd_text), and setting `preprocess_ok`
so downstream nodes/the graph's conditional edges can short-circuit on
failure instead of wasting an LLM call on bad input.
"""

from __future__ import annotations

from state import GraphState
from resume_extraction import (
    ResumeExtractionError,
    clean_job_description,
    extract_resume_text,
)


def preprocess_node(state: GraphState) -> dict:
    """LangGraph node function: reads resume_bytes + job_description from
    state, returns a partial state update.

    On extraction failure, sets preprocess_ok=False and appends a clear
    message to errors — does NOT raise. The graph's conditional edge
    (defined in app/graph/build.py, next file) decides whether to route
    to an early END based on this flag, so failure handling lives in one
    place (the graph wiring) rather than being duplicated across nodes.
    """
    errors: list[str] = list(state.get("errors", []))

    # --- Job description cleanup (cheap, can't really fail) ---
    jd_text = clean_job_description(state["job_description"])
    if not jd_text.strip():
        errors.append("Job description was empty after cleanup.")
        return {
            "jd_text": jd_text,
            "resume_text": "",
            "preprocess_ok": False,
            "errors": errors,
        }

    # --- Resume PDF extraction (can fail in several distinct ways) ---
    try:
        result = extract_resume_text(state["resume_bytes"])
    except ResumeExtractionError as exc:
        errors.append(str(exc))
        return {
            "jd_text": jd_text,
            "resume_text": "",
            "preprocess_ok": False,
            "errors": errors,
        }

    if result.truncated:
        errors.append(
            "Resume text was long and has been truncated for processing; "
            "analysis may miss content from the end of the document."
        )

    return {
        "jd_text": jd_text,
        "resume_text": result.text,
        "preprocess_ok": True,
        "errors": errors,
    }