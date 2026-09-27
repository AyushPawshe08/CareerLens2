"""
Auth routes: POST /api/auth/register, POST /api/auth/login, GET /api/auth/me.

Register/login both return a Token on success. Registration does NOT
auto-log-in by returning a token from a separate "session" concept —
issuing a JWT directly on successful registration is intentional here
(avoids forcing an immediate second login call), consistent with issuing
one on login.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_user
from security import create_access_token, hash_password, verify_password
from db_models import User
from auth_schema import Token, UserCreate, UserLogin, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> Token:
    existing = await db.scalar(select(User).where(User.email == payload.email))
    if existing is not None:
        # Deliberately vague-but-honest here (not a security-sensitive
        # detail like "wrong password") — telling the user an account
        # already exists is normal, expected UX for registration.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(subject=str(user.id))
    return Token(access_token=token)


@router.post("/login", response_model=Token)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)) -> Token:
    user = await db.scalar(select(User).where(User.email == payload.email))

    # Same error for "no such user" and "wrong password" — never let a
    # client distinguish these, or you've built a username enumeration
    # oracle (attacker can find out which emails are registered).
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if user is None:
        raise invalid_credentials
    if not verify_password(payload.password, user.hashed_password):
        raise invalid_credentials
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    token = create_access_token(subject=str(user.id))
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)) -> UserOut:
    """Returns the profile of whoever the Bearer token belongs to.
    Frontend uses this to restore session state (e.g. "logged in as...")
    after a page refresh, without re-sending credentials.
    """
    return UserOut(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at.isoformat(),
    )