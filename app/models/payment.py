from datetime import datetime, UTC
from enum import StrEnum

from sqlalchemy import Integer, ForeignKey, DateTime, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class PaymentStatus(StrEnum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default=PaymentStatus.PENDING.value,
        nullable=False,
    )

    amount: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        default="USD",
        nullable=False,
    )

    order: Mapped["Order"] = relationship(lazy="joined")
    user: Mapped["User"] = relationship(lazy="joined")
    items: Mapped[list["PaymentItem"]] = relationship(
        back_populates="payment",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
