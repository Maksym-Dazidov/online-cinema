from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.genre import Genre
from app.schemas.genre import GenreCreate


class GenreCRUD:
    async def get(self, db: AsyncSession, genre_id: int) -> Genre | None:
        stmt = select(Genre).where(Genre.id == genre_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession) -> list[Genre]:
        stmt = select(Genre).order_by(Genre.name)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, data: GenreCreate) -> Genre:
        stmt = select(Genre).where(Genre.name == data.name)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Genre with this name already exists"
            )

        genre = Genre(name=data.name)
        db.add(genre)
        await db.commit()
        await db.refresh(genre)
        return genre

    async def delete(self, db: AsyncSession, genre_id: int) -> None:
        genre = await self.get(db, genre_id)
        if genre:
            await db.delete(genre)
            await db.commit()


genre_crud = GenreCRUD()
