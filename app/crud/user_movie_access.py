from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_movie_access import UserMovieAccess
from app.models.order import Order


class UserMovieAccessCRUD:
    async def has_access(
            self,
            db: AsyncSession,
            user_id: int,
            movie_id: int,
    ) -> bool:
        stmt = select(UserMovieAccess).where(
            UserMovieAccess.user_id == user_id,
            UserMovieAccess.movie_id == movie_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def grant_for_order(
            self,
            db: AsyncSession,
            user_id: int,
            order_id: int,
            payment_id: int | None = None,
    ) -> None:
        stmt = select(Order).where(
            Order.id == order_id,
            Order.user_id == user_id,
        )
        order = (await db.execute(stmt)).scalar_one_or_none()
        if not order:
            return

        for item in order.items:
            exists_stmt = select(UserMovieAccess).where(
                UserMovieAccess.user_id == user_id,
                UserMovieAccess.movie_id == item.movie_id,
            )
            exists = (await db.execute(exists_stmt)).scalar_one_or_none()
            if exists:
                continue

            access = UserMovieAccess(
                user_id=user_id,
                movie_id=item.movie_id,
                order_id=order.id,
                payment_id=payment_id,
            )
            db.add(access)

        await db.commit()

    async def get_user_movies(
            self,
            db: AsyncSession,
            user_id: int,
    ) -> list[UserMovieAccess]:
        stmt = (
            select(UserMovieAccess)
            .where(UserMovieAccess.user_id == user_id)
            .order_by(UserMovieAccess.granted_at.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()


user_movie_access_crud = UserMovieAccessCRUD()
