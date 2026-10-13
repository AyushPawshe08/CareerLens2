from __future__ import annotations

import asyncio
import io
from dataclasses import dataclass

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from core.config import settings


class ResumeExtractionError(Exception):
    pass


@dataclass
class ExtractionResult:
    text: str
    page_count: int
    truncated: bool


async def extract_resume_text(resume_bytes: bytes) -> ExtractionResult:
    return await asyncio.to_thread(_extract_resume_text_sync, resume_bytes)


def _extract_resume_text_sync(resume_bytes: bytes) -> ExtractionResult:
    try:
        reader = PdfReader(io.BytesIO(resume_bytes))
    except PdfReadError as exc:
        raise ResumeExtractionError(
            "Couldn't read this file as a PDF. Please upload a valid PDF resume."
        ) from exc

    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception as exc:
            raise ResumeExtractionError(
                "This PDF is password-protected. Please upload an unprotected PDF."
            ) from exc

    page_count = len(reader.pages)
    if page_count == 0:
        raise ResumeExtractionError("This PDF appears to have no pages.")

    if page_count > settings.max_resume_pages:
        raise ResumeExtractionError(
            f"Resume has {page_count} pages; please keep it to "
            f"{settings.max_resume_pages} pages or fewer."
        )

    raw_text_parts = []
    for page in reader.pages:
        try:
            raw_text_parts.append(page.extract_text() or "")
        except Exception:
            continue

    text = "\n".join(part.strip() for part in raw_text_parts if part.strip())
    text = _normalize_whitespace_sync(text)

    if len(text) < settings.min_extracted_text_chars:
        raise ResumeExtractionError(
            "Couldn't extract readable text from this PDF. It may be a "
            "scanned image rather than a text-based document — please "
            "upload a text-based PDF (exported from Word/Docs, not scanned)."
        )

    truncated = False
    if len(text) > settings.max_resume_chars:
        text = text[: settings.max_resume_chars]
        truncated = True

    return ExtractionResult(text=text, page_count=page_count, truncated=truncated)


def _normalize_whitespace_sync(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


async def _normalize_whitespace(text: str) -> str:
    return await asyncio.to_thread(_normalize_whitespace_sync, text)


async def clean_job_description(jd_text: str) -> str:
    text = await _normalize_whitespace(jd_text)
    if len(text) > settings.max_jd_chars:
        text = text[: settings.max_jd_chars]
    return text