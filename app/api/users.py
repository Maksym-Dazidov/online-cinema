from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.crud.user_profile import user_profile_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserRead
from app.schemas.user_profile import UserProfileRead, UserProfileUpdate, UserProfileCreate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/me/profile", response_model=UserProfileRead | None)
async def get_my_profile(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    profile = await user_profile_crud.get_by_user_id(db, current_user.id)
    return profile


@router.patch("/me/profile", response_model=UserProfileRead)
async def update_my_profile(
        data: UserProfileUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    profile = await user_profile_crud.get_by_user_id(db, current_user.id)

    if profile is None:
        profile = await user_profile_crud.create_for_user(
            db=db,
            user_id=current_user.id,
            data=UserProfileCreate(**data.model_dump(exclude_unset=True)),
        )
        return profile

    profile = await user_profile_crud.update_for_user(db, profile, data)
    return profile
