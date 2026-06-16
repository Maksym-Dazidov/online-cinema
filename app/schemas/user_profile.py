from datetime import date
from pydantic import BaseModel, Field


class UserProfileBase(BaseModel):
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    avatar_url: str | None = Field(None, max_length=500)
    birth_date: date | None = None
    gender: str | None = Field(None, max_length=20)
    bio: str | None = None


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfileRead(BaseModel):
    id: int
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    avatar_url: str | None = Field(None, max_length=500)
    birth_date: date | None = None
    gender: str | None = Field(None, max_length=20)
    bio: str | None = None

    class Config:
        from_attributes = True
