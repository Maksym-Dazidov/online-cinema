from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_profile import UserProfile
from app.schemas.user_profile import UserProfileCreate, UserProfileUpdate


class UserProfileCRUD:
    async def get_by_user_id(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> UserProfile | None:
        stmt = select(UserProfile).where(UserProfile.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_for_user(
        self,
        db: AsyncSession,
        user_id: int,
        data: UserProfileCreate,
    ) -> UserProfile:
        profile = UserProfile(
            user_id=user_id,
            **data.model_dump(exclude_unset=True),
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        return profile

    async def update_for_user(
        self,
        db: AsyncSession,
        profile: UserProfile,
        data: UserProfileUpdate,
    ) -> UserProfile:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)

        await db.commit()
        await db.refresh(profile)
        return profile


user_profile_crud = UserProfileCRUD()
