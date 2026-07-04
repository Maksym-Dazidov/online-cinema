from datetime import datetime, UTC, timedelta
from sqlalchemy import Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ActivationToken(Base):
    __tablename__ = "activation_tokens"

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_activation_user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["User"] = relationship(lazy="joined")

    @staticmethod
    def generate_expiration(hours: int = 24) -> datetime:
        return datetime.now(UTC) + timedelta(hours=hours)
