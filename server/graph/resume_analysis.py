from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

from core.config import settings
from graph.llm_factory import get_structured_llm
from graph.state import GraphState
from models.schemas import ResumeAnalysis

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


async def resume_analysis_node(state: GraphState) -> dict:
    errors: list[str] = list(state.get("errors", []))

    structured_llm = get_structured_llm(ResumeAnalysis)
    chain = _prompt | structured_llm

    try:
        result: ResumeAnalysis = await chain.ainvoke(
            {
                "jd_text": state["jd_text"],
                "resume_text": state["resume_text"],
            }
        )
    except Exception as exc:
        errors.append(f"Resume analysis failed after trying all LLM providers: {exc}")
        return {
            "resume_analysis": None,
            "errors": errors,
        }

    return {
        "resume_analysis": result,
        "errors": errors,
    }