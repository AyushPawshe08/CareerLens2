from __future__ import annotations

from graph.state import GraphState
from graph.resume_extraction import (
    ResumeExtractionError,
    clean_job_description,
    extract_resume_text,
)


async def preprocess_node(state: GraphState) -> dict:
    errors: list[str] = list(state.get("errors", []))

    jd_text = await clean_job_description(state["job_description"])
    if not jd_text.strip():
        errors.append("Job description was empty after cleanup.")
        return {
            "jd_text": jd_text,
            "resume_text": "",
            "preprocess_ok": False,
            "errors": errors,
        }

    try:
        result = await extract_resume_text(state["resume_bytes"])
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