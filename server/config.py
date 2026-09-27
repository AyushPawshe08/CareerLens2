"""
Centralized application settings.

All config is loaded from environment variables (or a local .env file via
python-dotenv/pydantic-settings). Nothing else in the codebase should call
os.environ directly — import `settings` from here instead.
"""

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

    # -------------------------------------------------------------
    # Database (Neon Postgres)
    # -------------------------------------------------------------
    # Use the async driver form for SQLAlchemy: postgresql+asyncpg://...
    # Neon gives you a standard postgresql:// URL — swap the scheme prefix.
    database_url: str = Field(default="")
    db_echo: bool = False  # log every SQL statement — dev/debug only

    # -------------------------------------------------------------
    # Auth / JWT
    # -------------------------------------------------------------
    jwt_secret_key: str = Field(default="")  # MUST be set via env in any real deployment
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24  # 24h

    # -------------------------------------------------------------
    # App
    # -------------------------------------------------------------
    app_name: str = "CareerLens"
    environment: str = Field(default="development")  # development | staging | production
    debug: bool = True

    # -------------------------------------------------------------
    # LLM Provider API Keys
    # -------------------------------------------------------------
    groq_api_key: str = Field(default="")
    google_api_key: str = Field(default="")       # for Gemini

    # -------------------------------------------------------------
    # LLM Model Selection
    # -------------------------------------------------------------
    # Primary + fallback chain, in order. First is tried first.
    # Kept as simple strings here; the LLM factory (next file) maps
    # these to actual LangChain chat model instances.
    primary_provider: str = "groq"
    fallback_providers: List[str] = ["gemini"]

    groq_model: str = "llama-3.3-70b-versatile"
    gemini_model: str = "gemini-2.0-flash"

    llm_temperature: float = 0.3
    llm_max_retries: int = 2          # retries PER provider before falling back
    llm_request_timeout: int = 30     # seconds

    # -------------------------------------------------------------
    # Token / cost controls
    # -------------------------------------------------------------
    max_resume_chars: int = 8000      # truncate extracted resume text beyond this
    max_jd_chars: int = 4000          # truncate JD text beyond this
    max_output_tokens_resume: int = 1200
    max_output_tokens_questions: int = 1800

    # -------------------------------------------------------------
    # Resume upload constraints
    # -------------------------------------------------------------
    max_resume_pages: int = 2
    max_upload_size_mb: int = 5
    min_extracted_text_chars: int = 100  # below this -> treat extraction as failed

    # -------------------------------------------------------------
    # Caching
    # -------------------------------------------------------------
    cache_enabled: bool = True
    cache_ttl_seconds: int = 60 * 60 * 24  # 24h


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor — settings are read once per process."""
    return Settings()


settings = get_settings()