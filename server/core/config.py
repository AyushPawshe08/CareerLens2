from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(default="")
    db_echo: bool = False

    jwt_secret_key: str = Field(default="")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24

    app_name: str = "CareerLens"
    environment: str = Field(default="development")
    debug: bool = True

    groq_api_key: str = Field(default="")
    google_api_key: str = Field(default="")

    primary_provider: str = "groq"
    fallback_providers: List[str] = ["gemini"]

    groq_model: str = "llama-3.3-70b-versatile"
    gemini_model: str = "gemini-2.0-flash"

    llm_temperature: float = 0.3
    llm_max_retries: int = 2
    llm_request_timeout: int = 30

    max_resume_chars: int = 8000
    max_jd_chars: int = 4000
    max_output_tokens_resume: int = 1200
    max_output_tokens_questions: int = 1800

    max_resume_pages: int = 2
    max_upload_size_mb: int = 5
    min_extracted_text_chars: int = 100

    cache_enabled: bool = True
    cache_ttl_seconds: int = 60 * 60 * 24


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()