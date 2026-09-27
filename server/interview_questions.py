"""
Interview Question Generation node — third step in the pipeline.

Takes resume_text + jd_text + resume_analysis from state and generates
technical, HR, and behavioral questions in a SINGLE structured LLM call
(not three parallel calls) to save tokens and latency — see architecture
notes from the build discussion.
"""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

from llm_factory import get_structured_llm
from state import GraphState
from schemas import InterviewQuestions

_SYSTEM_PROMPT = """\
You are an experienced interview panelist who prepares candidates for \
interviews. Using the candidate's resume, the job description, and a prior \
analysis of the resume's fit against the JD, generate interview questions \
the candidate should practice.

Rules:
- technical: 4-6 questions probing the candidate's actual listed skills AND \
the JD's required skills — especially anything in `missing_skills`, since \
the candidate should be ready to address gaps.
- hr: 2-3 standard HR/logistics questions relevant to this specific role \
(not generic filler like "where do you see yourself in 5 years" unless \
genuinely relevant).
- behavioral: 3-4 STAR-style behavioral questions grounded in the \
candidate's actual resume content (specific projects/roles mentioned), not \
generic behavioral questions.
- For each question, fill `why_asked` with one short clause tying it back \
to a specific resume or JD detail.
- Assign `difficulty` honestly based on seniority implied by the JD.
- Do not repeat near-identical questions across categories.
"""

_HUMAN_PROMPT = """\
JOB DESCRIPTION:
{jd_text}

RESUME:
{resume_text}

RESUME ANALYSIS (already computed):
- Matched skills: {matched_skills}
- Missing skills: {missing_skills}
- Suggested roles: {suggested_roles}
"""

_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", _SYSTEM_PROMPT),
        ("human", _HUMAN_PROMPT),
    ]
)


def interview_questions_node(state: GraphState) -> dict:
    """LangGraph node function. Assumes resume_analysis is populated — the
    graph's conditional edge should prevent this node from running if the
    prior step failed.
    """
    errors: list[str] = list(state.get("errors", []))
    analysis = state.get("resume_analysis")

    if analysis is None:
        errors.append(
            "Interview question generation skipped: no resume analysis available."
        )
        return {"interview_questions": None, "errors": errors}

    structured_llm = get_structured_llm(InterviewQuestions)
    chain = _prompt | structured_llm

    try:
        result: InterviewQuestions = chain.invoke(
            {
                "jd_text": state["jd_text"],
                "resume_text": state["resume_text"],
                "matched_skills": ", ".join(analysis.matched_skills) or "none listed",
                "missing_skills": ", ".join(analysis.missing_skills) or "none listed",
                "suggested_roles": ", ".join(analysis.suggested_roles) or "none listed",
            }
        )
    except Exception as exc:
        errors.append(
            f"Interview question generation failed after trying all LLM providers: {exc}"
        )
        return {"interview_questions": None, "errors": errors}

    return {"interview_questions": result, "errors": errors}