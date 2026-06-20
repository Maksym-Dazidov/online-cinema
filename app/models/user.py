from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    group_id: Mapped[int] = mapped_column(ForeignKey("user_groups.id"), nullable=False)
    group: Mapped["UserGroup"] = relationship(back_populates="users", lazy="joined")

    profile: Mapped["UserProfile | None"] = relationship(
        back_populates="user",
        uselist=False,
        lazy="joined",
    )

    favorites: Mapped[list["Favorite"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    cart: Mapped["Cart | None"] = relationship(
        back_populates="user",
        uselist=False,
        lazy="joined",
    )

    orders: Mapped[list["Order"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
