"""
Resume Analysis node — second step in the pipeline.

Takes resume_text + jd_text from state, calls the LLM (via the fallback-
chained get_llm()) with structured output bound to the ResumeAnalysis
schema, and writes the result back to state.
"""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

from config import settings
from llm_factory import get_structured_llm
from state import GraphState
from schemas import ResumeAnalysis

_SYSTEM_PROMPT = """\
You are an expert technical recruiter and resume reviewer. Compare the \
candidate's resume against the job description and produce a structured \
analysis.

Rules:
- matched_skills: only skills that genuinely appear in BOTH the resume and \
the JD (don't infer skills that aren't stated).
- missing_skills: skills/requirements clearly stated in the JD that are NOT \
evidenced in the resume.
- suggested_roles: 1-3 job titles this resume is realistically a strong fit \
for, based on actual experience shown.
- recommendations: concrete, specific, actionable edits (e.g. "Quantify the \
impact of the caching project in bullet 3" — not generic advice like "add \
more detail").
- match_score: your honest 0-100 estimate of resume-to-JD fit.
- Be concise. Do not pad the response with filler.
"""

_HUMAN_PROMPT = """\
JOB DESCRIPTION:
{jd_text}

RESUME:
{resume_text}
"""

_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", _SYSTEM_PROMPT),
        ("human", _HUMAN_PROMPT),
    ]
)


def resume_analysis_node(state: GraphState) -> dict:
    """LangGraph node function. Assumes preprocess_ok is True — the graph's
    conditional edge should prevent this node from running otherwise.
    """
    errors: list[str] = list(state.get("errors", []))

    structured_llm = get_structured_llm(ResumeAnalysis)
    chain = _prompt | structured_llm

    try:
        result: ResumeAnalysis = chain.invoke(
            {
                "jd_text": state["jd_text"],
                "resume_text": state["resume_text"],
            }
        )
    except Exception as exc:
        # get_llm() already tried primary + all fallbacks internally; if we
        # land here, every provider failed. Surface a clear error and let
        # the graph decide how to proceed (likely: skip to an error END).
        errors.append(f"Resume analysis failed after trying all LLM providers: {exc}")
        return {
            "resume_analysis": None,
            "errors": errors,
        }

    return {
        "resume_analysis": result,
        "errors": errors,
    }