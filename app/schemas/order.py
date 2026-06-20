from datetime import datetime
from typing import List

from pydantic import BaseModel
from app.schemas.movie import MovieRead


class OrderItemRead(BaseModel):
    id: int
    movie: MovieRead
    price_at_order: float

    class Config:
        from_attributes = True


class OrderRead(BaseModel):
    id: int
    created_at: datetime
    status: str
    total_amount: float | None
    items: List[OrderItemRead]

    class Config:
        from_attributes = True
