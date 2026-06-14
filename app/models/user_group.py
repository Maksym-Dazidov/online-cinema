from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from app.db.session import Base


class UserGroup(Base):
    __tablename__ = "user_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    users: Mapped[list["User"]] = relationship(back_populates="group", lazy="selectin")
