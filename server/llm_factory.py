"""
LLM factory.

Builds a single LangChain "runnable" chat model that:
  1. Tries the primary provider first (Groq, by default).
  2. Automatically falls back to the next provider in the chain on failure,
     using LangChain's built-in `.with_fallbacks()`.
  3. Applies per-provider retries (via `.with_retry()`) before falling
     back, so a transient error doesn't burn a fallback slot unnecessarily.

This directly addresses "Problem 3: LLM failure" from the project spec —
callers just import `get_llm()` and never think about which provider
actually served the request.
"""

from __future__ import annotations

from typing import Dict, Type, TypeVar

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import Runnable
from pydantic import BaseModel

from config import settings

T = TypeVar("T", bound=BaseModel)

_PROVIDER_BUILDERS: Dict[str, "callable"] = {}


def _build_groq() -> BaseChatModel:
    from langchain_groq import ChatGroq

    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=settings.llm_temperature,
        timeout=settings.llm_request_timeout,
    )


def _build_gemini() -> BaseChatModel:
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        api_key=settings.google_api_key,
        model=settings.gemini_model,
        temperature=settings.llm_temperature,
        timeout=settings.llm_request_timeout,
    )


_PROVIDER_BUILDERS = {
    "groq": _build_groq,
    "gemini": _build_gemini,
}


def _build_raw_provider(name: str) -> BaseChatModel:
    """Build a bare chat model instance — NO retry/fallback wrapping.
    Callers apply .with_structured_output() (or use it plain) on this
    directly, since that method only exists on real BaseChatModel
    instances, not on the generic Runnable wrappers retry/fallbacks
    produce.
    """
    if name not in _PROVIDER_BUILDERS:
        raise ValueError(
            f"Unknown LLM provider '{name}'. Known providers: {list(_PROVIDER_BUILDERS)}"
        )
    return _PROVIDER_BUILDERS[name]()


def _provider_order() -> list[str]:
    order = [settings.primary_provider, *settings.fallback_providers]
    seen = set()
    return [p for p in order if not (p in seen or seen.add(p))]


_plain_llm_singleton: Runnable | None = None


def get_llm() -> Runnable:
    """Plain (non-structured-output) fallback-chained LLM, for free-text
    generation use cases. Retry/fallback wrapping is safe here because
    nothing downstream needs .with_structured_output() on the result.
    """
    global _plain_llm_singleton
    if _plain_llm_singleton is not None:
        return _plain_llm_singleton

    order = _provider_order()
    built = [
        _build_raw_provider(name).with_retry(stop_after_attempt=settings.llm_max_retries)
        for name in order
    ]
    primary, *fallbacks = built
    _plain_llm_singleton = primary.with_fallbacks(fallbacks) if fallbacks else primary
    return _plain_llm_singleton


_structured_llm_cache: Dict[str, Runnable] = {}


def get_structured_llm(schema: Type[T]) -> Runnable:
    """Return a fallback-chained LLM bound to a structured output schema.

    This is what LangGraph agent nodes should use instead of
    get_llm().with_structured_output(schema) — that pattern is broken
    because with_retry()/with_fallbacks() return generic Runnables that
    don't expose with_structured_output.

    Correct order per provider: build raw model -> bind structured output
    -> wrap with retry. THEN chain providers together with fallbacks.
    """
    cache_key = schema.__name__
    if cache_key in _structured_llm_cache:
        return _structured_llm_cache[cache_key]

    order = _provider_order()
    built = [
        _build_raw_provider(name)
        .with_structured_output(schema, method="function_calling")
        .with_retry(stop_after_attempt=settings.llm_max_retries)
        for name in order
    ]
    primary, *fallbacks = built
    chained = primary.with_fallbacks(fallbacks) if fallbacks else primary
    _structured_llm_cache[cache_key] = chained
    return chained


def get_llm_for_provider(name: str) -> BaseChatModel:
    """Escape hatch: get a single named provider directly, no fallback chain.
    Useful for testing a specific provider in isolation.
    """
    return _build_raw_provider(name)