from __future__ import annotations

from typing import Dict, Type, TypeVar

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import Runnable
from pydantic import BaseModel

from core.config import settings

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
    return _build_raw_provider(name)