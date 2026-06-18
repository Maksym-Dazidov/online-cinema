from datetime import datetime
from pydantic import BaseModel

from app.schemas.movie import MovieRead


class FavoriteRead(BaseModel):
    id: int
    movie: MovieRead
    created_at: datetime

    class Config:
        from_attributes = True
