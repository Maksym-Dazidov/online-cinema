from datetime import datetime

from pydantic import BaseModel

from app.schemas.movie import MovieRead


class UserMovieAccessRead(BaseModel):
    id: int
    movie: MovieRead
    granted_at: datetime

    class Config:
        from_attributes = True
