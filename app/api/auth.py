from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.crud.activation_token import activation_token_crud
from app.crud.password_reset_token import password_reset_token_crud
from app.schemas.user import UserCreate
from app.schemas.auth import (
    LoginSchema,
    TokenSchema,
    RefreshTokenSchema,
    EmailSchema,
    PasswordResetConfirmSchema
)
from app.services.auth import auth_service
from app.crud.user import user_crud
from app.db.session import get_db
from app.services.email import email_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(
        user_in: UserCreate,
        db: AsyncSession = Depends(get_db),
):
    existing = await user_crud.get_by_email(db, user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = await user_crud.create(db, user_in)

    token_obj, raw_token = await activation_token_crud.create_or_replace(db, user.id)

    await email_service.send_activation_email(user.email, raw_token)

    return {"message": "Activation email sent"}


@router.get("/activate")
async def activate_account(
        token: str,
        db: AsyncSession = Depends(get_db),
):
    token_obj = await activation_token_crud.get_by_token(db, token)
    if not token_obj:
        raise HTTPException(400, "Invalid token")

    if token_obj.expires_at < datetime.now(UTC):
        raise HTTPException(400, "Token expired")

    user = token_obj.user
    user.is_active = True

    await db.commit()
    await db.refresh(user)

    await activation_token_crud.delete(db, token_obj)

    return {"message": "Account activated"}


@router.post("/resend-activation")
async def resend_activation(
        email_obj: EmailSchema,
        db: AsyncSession = Depends(get_db),
):
    user = await user_crud.get_by_email(db, email_obj.email)
    if not user:
        return {"message": "If the account exists, an activation link has been sent"}

    if user.is_active:
        raise HTTPException(400, "User already active")

    token_obj, raw_token = await activation_token_crud.create_or_replace(db, user.id)
    await email_service.send_activation_email(user.email, raw_token)

    return {"message": "If the account exists, an activation link has been sent"}


@router.post("/request-password-reset")
async def request_password_reset(
        email_obj: EmailSchema,
        db: AsyncSession = Depends(get_db),
):
    user = await user_crud.get_by_email(db, email_obj.email)
    if not user or not user.is_active:
        return {"message": "If the account exists, a reset link has been sent"}

    token_obj, raw_token = await password_reset_token_crud.create_or_replace(db, user.id)
    await email_service.send_password_reset_email(user.email, raw_token)
    return {"message": "If the account exists, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
        token: str,
        data: PasswordResetConfirmSchema,
        db: AsyncSession = Depends(get_db),
):
    token_obj = await password_reset_token_crud.get_by_token(db, token)
    if not token_obj or token_obj.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = token_obj.user
    user.hashed_password = get_password_hash(data.new_password)

    await db.commit()
    await db.refresh(user)

    await password_reset_token_crud.delete(db, token_obj)

    return {"message": "Password updated"}


@router.post("/login", response_model=TokenSchema)
async def login(
        data: LoginSchema,
        db: AsyncSession = Depends(get_db),
):
    user = await auth_service.authenticate_user(
        db=db,
        email=data.email,
        password=data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    tokens = await auth_service.create_tokens_for_user(user)
    return tokens


@router.post("/refresh", response_model=TokenSchema)
async def refresh_tokens(
        data: RefreshTokenSchema,
        db: AsyncSession = Depends(get_db),
):
    user_id = auth_service.validate_refresh_token(data.refresh_token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user = await user_crud.get(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    tokens = await auth_service.create_tokens_for_user(user)
    return tokens
