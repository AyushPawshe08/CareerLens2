"""
Auth dependency: get_current_user.

Import and use this on any route that requires a logged-in user:

    @router.get("/something")
    async def something(user: User = Depends(get_current_user)):
        ...

Reads the JWT from the `Authorization: Bearer <token>` header (via
FastAPI's OAuth2PasswordBearer, which just extracts that header — we are
NOT using OAuth2 password flow itself, only reusing its header-parsing
convenience), validates it, and loads the corresponding User row.
"""

from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from security import TokenError, decode_access_token
from db_models import User

# tokenUrl is only used by FastAPI's auto-generated OpenAPI docs (the
# "Authorize" button) to know where to POST for a token — it does not
# affect how this dependency actually validates tokens.
_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials.",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    token: str = Depends(_oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        user_id_str = decode_access_token(token)
        user_id = uuid.UUID(user_id_str)
    except (TokenError, ValueError):
        # ValueError covers a malformed (non-UUID) subject claim, which
        # would otherwise raise INSIDE the try below in a confusing way.
        raise _credentials_exception

    user = await db.get(User, user_id)
    if user is None:
        raise _credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    return user