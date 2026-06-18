from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate


class ReviewCRUD:
    async def get(self, db: AsyncSession, review_id: int) -> Review | None:
        stmt = select(Review).where(Review.id == review_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_for_movie(self, db: AsyncSession, movie_id: int) -> list[Review]:
        stmt = select(Review).where(Review.movie_id == movie_id)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(
            self,
            db: AsyncSession,
            user_id: int,
            movie_id: int,
            data: ReviewCreate,
    ) -> Review:
        stmt = select(Review).where(
            Review.user_id == user_id,
            Review.movie_id == movie_id,
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already reviewed this movie",
            )

        review = Review(
            user_id=user_id,
            movie_id=movie_id,
            rating=data.rating,
            text=data.text,
        )

        db.add(review)
        await db.commit()
        await db.refresh(review)
        return review

    async def update(
            self,
            db: AsyncSession,
            review: Review,
            data: ReviewUpdate,
    ) -> Review:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(review, field, value)

        await db.commit()
        await db.refresh(review)
        return review

    async def delete(self, db: AsyncSession, review: Review) -> None:
        await db.delete(review)
        await db.commit()


review_crud = ReviewCRUD()
