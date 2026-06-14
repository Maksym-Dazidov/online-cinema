from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.crud.user_group import user_group_crud


class UserCRUD:
    async def get(self, db: AsyncSession, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
        stmt = select(User).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: UserCreate) -> User:
        hashed_password = get_password_hash(obj_in.password)

        group = await user_group_crud.get_by_name(db, "user")

        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        user = User(
            email=obj_in.email,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
            group_id=group.id,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def update(self, db: AsyncSession, db_obj: User, obj_in: UserUpdate) -> User:
        if obj_in.email is not None:
            db_obj.email = obj_in.email

        if obj_in.password is not None:
            db_obj.hashed_password = get_password_hash(obj_in.password)

        if obj_in.is_active is not None:
            db_obj.is_active = obj_in.is_active

        if obj_in.is_superuser is not None:
            db_obj.is_superuser = obj_in.is_superuser

        await db.commit()
        await db.refresh(db_obj)
        return db_obj


user_crud = UserCRUD()
