from __future__ import annotations

import asyncio

from langgraph.graph import END, START, StateGraph

from graph.interview_questions import interview_questions_node
from graph.preprocess import preprocess_node
from graph.resume_analysis import resume_analysis_node
from graph.state import GraphState


def _route_after_preprocess(state: GraphState) -> str:
    return "parallel_analysis" if state.get("preprocess_ok") else END


async def parallel_analysis_node(state: GraphState) -> dict:
    errors: list[str] = list(state.get("errors", []))

    results = await asyncio.gather(
        resume_analysis_node(state),
        interview_questions_node(state),
        return_exceptions=True,
    )

    resume_analysis_result = results[0]
    interview_questions_result = results[1]

    if isinstance(resume_analysis_result, Exception):
        errors.append(f"Resume analysis failed: {resume_analysis_result}")
        resume_analysis_data = {"resume_analysis": None}
    else:
        resume_analysis_data = resume_analysis_result
        errors.extend(resume_analysis_data.get("errors", []))

    if isinstance(interview_questions_result, Exception):
        errors.append(f"Interview questions failed: {interview_questions_result}")
        interview_questions_data = {"interview_questions": None}
    else:
        interview_questions_data = interview_questions_result
        errors.extend(interview_questions_data.get("errors", []))

    return {
        **resume_analysis_data,
        **interview_questions_data,
        "errors": errors,
    }


def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("preprocess", preprocess_node)
    graph.add_node("parallel_analysis", parallel_analysis_node)

    graph.add_edge(START, "preprocess")

    graph.add_conditional_edges(
        "preprocess",
        _route_after_preprocess,
        {"parallel_analysis": "parallel_analysis", END: END},
    )

    graph.add_edge("parallel_analysis", END)

    return graph.compile()


compiled_graph = build_graph()