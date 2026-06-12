from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.actor import Actor
from app.schemas.actor import ActorCreate


class ActorCRUD:
    async def get(self, db: AsyncSession, actor_id: int) -> Actor | None:
        stmt = select(Actor).where(Actor.id == actor_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession) -> list[Actor]:
        stmt = select(Actor).order_by(Actor.full_name)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, data: ActorCreate) -> Actor:
        actor = Actor(
            full_name=data.full_name,
            photo_url=data.photo_url,
        )
        db.add(actor)
        await db.commit()
        await db.refresh(actor)
        return actor

    async def delete(self, db: AsyncSession, actor_id: int) -> None:
        actor = await self.get(db, actor_id)
        if actor:
            await db.delete(actor)
            await db.commit()


actor_crud = ActorCRUD()
