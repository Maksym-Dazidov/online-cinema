from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_group import UserGroup


class UserGroupCRUD:
    async def get(self, db: AsyncSession, group_id: int) -> UserGroup | None:
        stmt = select(UserGroup).where(UserGroup.id == group_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, db: AsyncSession, name: str) -> UserGroup | None:
        stmt = select(UserGroup).where(UserGroup.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession) -> list[UserGroup]:
        stmt = select(UserGroup).order_by(UserGroup.id)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, name: str) -> UserGroup:
        group = UserGroup(name=name)
        db.add(group)
        await db.commit()
        await db.refresh(group)
        return group

    async def create_default_groups(self, db: AsyncSession) -> None:
        stmt = insert(UserGroup).values(
            [{"name": name} for name in ("user", "moderator", "admin")]
        )
        stmt = stmt.on_conflict_do_nothing(index_elements=[UserGroup.name])
        await db.execute(stmt)
        await db.commit()


user_group_crud = UserGroupCRUD()
