from datetime import datetime
from typing import List

from pydantic import BaseModel
from app.schemas.order import OrderRead


class PaymentItemRead(BaseModel):
    id: int
    amount: float

    class Config:
        from_attributes = True


class PaymentRead(BaseModel):
    id: int
    order: OrderRead
    user_id: int
    created_at: datetime
    status: str
    amount: float
    currency: str
    items: List[PaymentItemRead]

    class Config:
        from_attributes = True
