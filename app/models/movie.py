from sqlalchemy import String, Integer, ForeignKey, Table, Column, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.session import Base

movie_genres = Table(
    "movie_genres",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
)

movie_actors = Table(
    "movie_actors",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("actor_id", ForeignKey("actors.id", ondelete="CASCADE"), primary_key=True),
)


class Movie(Base):
    __tablename__ = "movies"

    __table_args__ = (
        UniqueConstraint("title", "year", name="uq_movie_title_year"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[float | None] = mapped_column(nullable=True)
    poster_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    trailer_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    price: Mapped[float] = mapped_column(nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    is_for_sale: Mapped[bool] = mapped_column(Boolean, default=True)
    is_free: Mapped[bool] = mapped_column(Boolean, default=False)

    genres: Mapped[list["Genre"]] = relationship(
        secondary=movie_genres,
        back_populates="movies",
        lazy="selectin",
    )

    actors: Mapped[list["Actor"]] = relationship(
        secondary=movie_actors,
        back_populates="movies",
        lazy="selectin",
    )
