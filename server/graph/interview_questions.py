from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

from graph.llm_factory import get_structured_llm
from graph.state import GraphState
from models.schemas import InterviewQuestions

_SYSTEM_PROMPT = """\
You are an experienced interview panelist who prepares candidates for \
interviews. Using the candidate's resume and the job description, first \
analyze the resume-JD fit internally, then generate interview questions \
the candidate should practice.

Internal Analysis (do NOT output this):
- Identify skills present in both resume and JD (matched skills)
- Identify skills required by JD but not in resume (missing skills)
- Determine 1-3 suitable job titles based on actual experience
- Estimate overall fit score (0-100)

Question Generation Rules:
- technical: 4-6 questions probing the candidate's actual listed skills AND \
the JD's required skills — especially focus on identified missing skills, \
since the candidate should be ready to address gaps.
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

Generate interview questions based on your internal analysis of the resume-JD fit.
"""

_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", _SYSTEM_PROMPT),
        ("human", _HUMAN_PROMPT),
    ]
)


async def interview_questions_node(state: GraphState) -> dict:
    errors: list[str] = list(state.get("errors", []))

    structured_llm = get_structured_llm(InterviewQuestions)
    chain = _prompt | structured_llm

    try:
        result: InterviewQuestions = await chain.ainvoke(
            {
                "jd_text": state["jd_text"],
                "resume_text": state["resume_text"],
            }
        )
    except Exception as exc:
        errors.append(
            f"Interview question generation failed after trying all LLM providers: {exc}"
        )
        return {"interview_questions": None, "errors": errors}

    return {"interview_questions": result, "errors": errors}