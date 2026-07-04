from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.activation_token import activation_token_crud
from app.schemas.user import UserCreate
from app.schemas.auth import LoginSchema, TokenSchema, RefreshTokenSchema, EmailSchema
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

    token_obj = await activation_token_crud.create_or_replace(db, user.id)

    await email_service.send_activation_email(user.email, token_obj.token)

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

    await activation_token_crud.delete(db, token_obj)
    await db.commit()
    await db.refresh(user)

    return {"message": "Account activated"}


@router.post("/resend-activation")
async def resend_activation(
        email_obj: EmailSchema,
        db: AsyncSession = Depends(get_db),
):
    email = email_obj.email

    user = await user_crud.get_by_email(db, email)
    if not user:
        raise HTTPException(404, "User not found")

    if user.is_active:
        raise HTTPException(400, "User already active")

    token_obj = await activation_token_crud.create_or_replace(db, user.id)
    await email_service.send_activation_email(user.email, token_obj.token)

    return {"message": "Activation email resent"}


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
