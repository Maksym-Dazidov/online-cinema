from datetime import datetime
from pydantic import BaseModel, Field


class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=10)
    text: str | None = None


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    rating: int | None = Field(None, ge=1, le=10)
    text: str | None = None


class ReviewRead(BaseModel):
    id: int
    user_id: int
    movie_id: int
    rating: int
    text: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
