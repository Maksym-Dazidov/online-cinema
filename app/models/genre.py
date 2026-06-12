from sqlalchemy import String, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.session import Base
from app.models.movie import movie_genres


class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    movies: Mapped[list["Movie"]] = relationship(
        secondary=movie_genres,
        back_populates="genres",
        lazy="selectin",
    )
