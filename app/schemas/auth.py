from pydantic import BaseModel, EmailStr, Field


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class EmailSchema(BaseModel):
    email: EmailStr


class PasswordResetConfirmSchema(BaseModel):
    new_password: str = Field(..., min_length=8)
