from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.movie import Movie
from app.models.genre import Genre
from app.models.actor import Actor
from app.schemas.movie import MovieCreate, MovieUpdate


class MovieCRUD:
    async def get(self, db: AsyncSession, movie_id: int) -> Movie | None:
        stmt = (
            select(Movie)
            .where(Movie.id == movie_id)
            .options(
                selectinload(Movie.genres),
                selectinload(Movie.actors),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession) -> list[Movie]:
        stmt = (
            select(Movie)
            .options(
                selectinload(Movie.genres),
                selectinload(Movie.actors),
            )
            .order_by(Movie.title)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, data: MovieCreate) -> Movie:
        stmt = select(Movie).where(
            Movie.title == data.title,
            Movie.year == data.year
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Movie with this title and year already exists"
            )

        movie = Movie(
            title=data.title,
            description=data.description,
            year=data.year,
            rating=data.rating,
            poster_url=data.poster_url,
            trailer_url=data.trailer_url,
            is_published=data.is_published,
            price=data.price,
            currency=data.currency,
            is_for_sale=data.is_for_sale,
            is_free=data.is_free,
        )

        if data.genre_ids:
            stmt = select(Genre).where(Genre.id.in_(data.genre_ids))
            genres = (await db.execute(stmt)).scalars().all()
            movie.genres = genres

        if data.actor_ids:
            stmt = select(Actor).where(Actor.id.in_(data.actor_ids))
            actors = (await db.execute(stmt)).scalars().all()
            movie.actors = actors

        db.add(movie)
        await db.commit()
        await db.refresh(movie)
        return movie

    async def update(self, db: AsyncSession, movie: Movie, data: MovieUpdate) -> Movie:
        for field, value in data.model_dump(exclude_unset=True).items():
            if field in ("genre_ids", "actor_ids"):
                continue
            setattr(movie, field, value)

        if data.genre_ids is not None:
            stmt = select(Genre).where(Genre.id.in_(data.genre_ids))
            movie.genres = (await db.execute(stmt)).scalars().all()

        if data.actor_ids is not None:
            stmt = select(Actor).where(Actor.id.in_(data.actor_ids))
            movie.actors = (await db.execute(stmt)).scalars().all()

        await db.commit()
        await db.refresh(movie)
        return movie

    async def delete(self, db: AsyncSession, movie: Movie) -> None:
        await db.delete(movie)
        await db.commit()


movie_crud = MovieCRUD()
