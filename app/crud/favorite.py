from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.favorite import Favorite


class FavoriteCRUD:
    async def add(self, db: AsyncSession, user_id: int, movie_id: int) -> Favorite:
        stmt = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.movie_id == movie_id,
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Movie already in favorites",
            )

        fav = Favorite(user_id=user_id, movie_id=movie_id)
        db.add(fav)
        await db.commit()
        await db.refresh(fav)
        return fav

    async def remove(self, db: AsyncSession, user_id: int, movie_id: int) -> None:
        stmt = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.movie_id == movie_id,
        )
        fav = (await db.execute(stmt)).scalar_one_or_none()

        if not fav:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Favorite not found",
            )

        await db.delete(fav)
        await db.commit()

    async def get_for_user(self, db: AsyncSession, user_id: int) -> list[Favorite]:
        stmt = select(Favorite).where(Favorite.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().all()


favorite_crud = FavoriteCRUD()
