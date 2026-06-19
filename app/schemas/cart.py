from datetime import datetime
from pydantic import BaseModel
from typing import List

from app.schemas.movie import MovieRead


class CartItemRead(BaseModel):
    id: int
    movie: MovieRead
    added_at: datetime

    class Config:
        from_attributes = True


class CartRead(BaseModel):
    id: int
    items: List[CartItemRead]

    class Config:
        from_attributes = True
