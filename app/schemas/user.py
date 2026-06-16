from pydantic import BaseModel, EmailStr, Field
from app.schemas.user_group import UserGroupRead
from app.schemas.user_profile import UserProfileRead


class UserBase(BaseModel):
    email: EmailStr = Field(..., max_length=255)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=255)


class UserUpdate(BaseModel):
    email: EmailStr | None = Field(None, max_length=255)
    password: str | None = Field(None, min_length=8, max_length=255)
    is_active: bool | None = None
    is_superuser: bool | None = None


class UserRead(BaseModel):
    id: int
    email: EmailStr = Field(..., max_length=255)
    is_active: bool
    is_superuser: bool
    group: UserGroupRead
    profile: UserProfileRead | None = None

    class Config:
        from_attributes = True
