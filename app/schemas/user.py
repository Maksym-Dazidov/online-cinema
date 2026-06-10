from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr = Field(..., max_length=255)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=255)


class UserUpdate(BaseModel):
    email: EmailStr | None = Field(None, max_length=255)
    password: str | None = Field(None, min_length=8, max_length=255)
    is_active: bool | None = None
    is_superuser: bool | None = None


class UserRead(UserBase):
    id: int
    is_active: bool
    is_superuser: bool

    model_config = {
        "from_attributes": True
    }


class UserInDB(UserRead):
    hashed_password: str
