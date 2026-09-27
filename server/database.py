"""
Database engine + session setup (Neon Postgres, async).

Everything else in the app that touches the DB should import `get_db`
(a FastAPI dependency yielding an AsyncSession) rather than creating
engines/sessions itself.
"""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config import settings


class Base(DeclarativeBase):
    """Base class for all ORM models (app/models/db_models.py)."""


# Neon connection strings often include psycopg2-style query params
# (sslmode=require, channel_binding=require) that asyncpg does NOT
# understand as URL params — they must be stripped from the URL and SSL
# enabled via connect_args instead. Keep DATABASE_URL in .env as a bare
# postgresql+asyncpg://user:password@host/dbname string, no "?..." suffix.
engine = create_async_engine(
    settings.database_url,
    echo=settings.db_echo,
    pool_pre_ping=True,
    connect_args={"ssl": "require"},
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields a session, guarantees it's closed after
    the request, and rolls back on any unhandled exception so a failed
    request never leaves a half-committed transaction hanging around.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """Create all tables if they don't exist yet.

    Fine for early development; once the schema stabilizes, switch to
    Alembic migrations instead of calling this on every startup — this
    function does NOT handle schema changes to existing tables, only
    creates missing ones.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)