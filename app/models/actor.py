from sqlalchemy import String, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.session import Base
from app.models.movie import movie_actors


class Actor(Base):
    __tablename__ = "actors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    movies: Mapped[list["Movie"]] = relationship(
        secondary=movie_actors,
        back_populates="actors",
        lazy="selectin",
    )
