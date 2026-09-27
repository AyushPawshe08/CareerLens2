"""
Auth primitives: password hashing and JWT create/verify.

Deliberately has ZERO knowledge of FastAPI, routes, or the DB — pure
functions only, so they're trivial to unit test and reused identically by
both the auth routes (login/register) and the get_current_user dependency.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pwdlib import PasswordHash

from config import settings

# pwdlib's recommended() hasher defaults to argon2 with sane parameters.
# Using this rather than hand-rolling argon2 params directly.
_password_hasher = PasswordHash.recommended()


# ---------------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------------

def hash_password(plain_password: str) -> str:
    return _password_hasher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _password_hasher.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------

class TokenError(Exception):
    """Raised for any invalid/expired/malformed token. Callers (the
    get_current_user dependency) should catch this and return a 401 —
    never leak WHY a token is invalid to the client (expired vs tampered
    vs malformed should all look the same from outside)."""


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT. `subject` is typically the user's id (as a str)
    — kept generic/minimal on purpose; don't put sensitive data in the
    payload, JWTs are signed but NOT encrypted, anyone can decode and read
    the payload without the secret.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str:
    """Decode + validate a JWT, returning the subject (user id) on success.
    Raises TokenError on any failure (expired, bad signature, malformed).
    """
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenError("Token has expired.") from exc
    except jwt.InvalidTokenError as exc:
        raise TokenError("Invalid token.") from exc

    subject = payload.get("sub")
    if subject is None:
        raise TokenError("Token missing subject.")
    return subject