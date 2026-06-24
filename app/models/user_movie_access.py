from datetime import datetime, UTC

from sqlalchemy import (
    Integer,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class UserMovieAccess(Base):
    __tablename__ = "user_movie_access"

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="uq_user_movie_access"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False,
    )
    order_id: Mapped[int | None] = mapped_column(
        ForeignKey("orders.id", ondelete="SET NULL"),
        nullable=True,
    )
    payment_id: Mapped[int | None] = mapped_column(
        ForeignKey("payments.id", ondelete="SET NULL"),
        nullable=True,
    )

    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    user: Mapped["User"] = relationship(lazy="joined")
    movie: Mapped["Movie"] = relationship(lazy="joined")
