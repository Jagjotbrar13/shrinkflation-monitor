from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from api.auth.demo import DEMO_EMAIL, DEMO_PASSWORD, DEMO_USER_ID, demo_user_model
from api.auth.dependencies import get_current_user
from api.auth.jwt import create_token, decode_token
from api.auth.security import hash_password, verify_password
from api.config import get_settings
from api.database import get_db
from api.models import User
from api.schemas import LoginIn, RegisterIn, TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _issue_tokens(user: User, response: Response) -> TokenOut:
    settings = get_settings()
    access_token = create_token(
        str(user.id), timedelta(minutes=settings.access_token_expire_minutes), "access"
    )
    refresh_token = create_token(
        str(user.id), timedelta(days=settings.refresh_token_expire_days), "refresh"
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=settings.app_env == "production",
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )
    return TokenOut(access_token=access_token, user=UserOut.model_validate(user))


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, response: Response, db: Session = Depends(get_db)) -> TokenOut:
    try:
        existing = db.query(User).filter(User.email == payload.email.lower()).one_or_none()
    except SQLAlchemyError:
        if payload.email.lower() == DEMO_EMAIL:
            return _issue_tokens(demo_user_model(), response)
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable. Use demo@grocerydemo.com / password123.",
        ) from None
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        location=payload.location.lower(),
        preferred_stores=payload.preferred_stores,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _issue_tokens(user, response)


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, response: Response, db: Session = Depends(get_db)) -> TokenOut:
    if payload.email.lower() == DEMO_EMAIL and payload.password == DEMO_PASSWORD:
        return _issue_tokens(demo_user_model(), response)

    try:
        user = db.query(User).filter(User.email == payload.email.lower()).one_or_none()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable. Use demo@grocerydemo.com / password123.",
        ) from exc
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return _issue_tokens(user, response)


@router.post("/refresh", response_model=TokenOut)
def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> TokenOut:
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    try:
        payload = decode_token(refresh_token, "refresh")
        user_id = UUID(str(payload["sub"]))
        if user_id == DEMO_USER_ID:
            return _issue_tokens(demo_user_model(), response)
        user = db.get(User, user_id)
    except (KeyError, ValueError, SQLAlchemyError) as exc:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from exc
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return _issue_tokens(user, response)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie("refresh_token")


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user
