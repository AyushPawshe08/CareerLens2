"""
Resume PDF extraction service.

Pure I/O + parsing logic — no LLM calls here. Responsible for:
  1. Enforcing the "max 2 pages" resume constraint from the spec.
  2. Extracting text via pypdf.
  3. Detecting a "garbage" extraction (e.g. scanned/image-only PDF) early,
     so we never silently send near-empty text to the LLM (problem flagged
     in the architecture review).
"""

from __future__ import annotations

import io
from dataclasses import dataclass

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from config import settings


class ResumeExtractionError(Exception):
    """Raised for any unrecoverable resume extraction failure.
    The API layer should catch this and return a clear 4xx to the user
    (never let it bubble up as an opaque 500).
    """


@dataclass
class ExtractionResult:
    text: str
    page_count: int
    truncated: bool  # True if text was cut down to max_resume_chars


def extract_resume_text(resume_bytes: bytes) -> ExtractionResult:
    """Extract text from a resume PDF.

    Raises ResumeExtractionError if:
      - the file isn't a readable PDF
      - it exceeds the configured max page count
      - the extracted text is suspiciously short (likely a scanned/image PDF
        with no text layer — pypdf can't OCR)
    """
    try:
        reader = PdfReader(io.BytesIO(resume_bytes))
    except PdfReadError as exc:
        raise ResumeExtractionError(
            "Couldn't read this file as a PDF. Please upload a valid PDF resume."
        ) from exc

    if reader.is_encrypted:
        # Try an empty-password unlock (common for "restricted" but not
        # truly password-protected exports); if that fails, bail clearly.
        try:
            reader.decrypt("")
        except Exception as exc:  # pypdf raises varied exception types here
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
            # A single malformed page shouldn't kill the whole extraction —
            # skip it and keep going with what we can read.
            continue

    text = "\n".join(part.strip() for part in raw_text_parts if part.strip())
    text = _normalize_whitespace(text)

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


def _normalize_whitespace(text: str) -> str:
    """Collapse excessive blank lines/spaces that bloat token count without
    adding signal (common artifact of column-based resume layouts)."""
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]  # drop empty lines
    return "\n".join(lines)


def clean_job_description(jd_text: str) -> str:
    """Lightweight cleanup + truncation for the pasted JD text."""
    text = _normalize_whitespace(jd_text)
    if len(text) > settings.max_jd_chars:
        text = text[: settings.max_jd_chars]
    return text