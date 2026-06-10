from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate
from app.schemas.auth import LoginSchema, TokenSchema
from app.services.auth import auth_service
from app.crud.user import user_crud
from app.db.session import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenSchema)
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

    tokens = await auth_service.create_tokens_for_user(user)
    return tokens


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
