"""
Graph assembly.

Wires together:

    START -> preprocess -> [conditional] -> resume_analysis
                 |                               |
                 v                               v
           (preprocess_ok=False)         [conditional]
                 |                               |
                 v                               v
                END                     interview_questions -> END
                                                  |
                                          (analysis failed)
                                                  |
                                                  v
                                                 END

Conditional edges short-circuit the graph on failure so we never waste an
LLM call on bad input (preprocess failure) or on a step whose required
input is missing (interview questions needs resume_analysis).
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from interview_questions import interview_questions_node
from preprocess import preprocess_node
from resume_analysis import resume_analysis_node
from state import GraphState


def _route_after_preprocess(state: GraphState) -> str:
    """If preprocessing failed (bad PDF, empty JD, etc.), skip straight to
    END rather than spending an LLM call on unusable input."""
    return "resume_analysis" if state.get("preprocess_ok") else END


def _route_after_resume_analysis(state: GraphState) -> str:
    """If every LLM provider failed for resume analysis, there's nothing
    useful to feed interview question generation — skip to END."""
    return "interview_questions" if state.get("resume_analysis") is not None else END


def build_graph():
    """Build and compile the CareerLens LangGraph pipeline.

    Returns a compiled graph with an `.invoke(state)` / `.ainvoke(state)`
    interface. Call this once (e.g. at app startup) and reuse the compiled
    graph — don't rebuild it per-request.
    """
    graph = StateGraph(GraphState)

    graph.add_node("preprocess", preprocess_node)
    graph.add_node("resume_analysis", resume_analysis_node)
    graph.add_node("interview_questions", interview_questions_node)

    graph.add_edge(START, "preprocess")

    graph.add_conditional_edges(
        "preprocess",
        _route_after_preprocess,
        {"resume_analysis": "resume_analysis", END: END},
    )

    graph.add_conditional_edges(
        "resume_analysis",
        _route_after_resume_analysis,
        {"interview_questions": "interview_questions", END: END},
    )

    graph.add_edge("interview_questions", END)

    return graph.compile()


# Built once at import time and reused across requests — LangGraph's
# compiled graph is stateless/thread-safe to invoke concurrently as long
# as each call passes its own state.
compiled_graph = build_graph()