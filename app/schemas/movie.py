from pydantic import BaseModel
from typing import List

from app.schemas.genre import GenreRead
from app.schemas.actor import ActorRead


class MovieBase(BaseModel):
    title: str
    description: str | None = None
    year: int
    rating: float | None = None
    poster_url: str | None = None
    trailer_url: str | None = None
    is_published: bool = True

    price: float
    currency: str = "USD"
    is_for_sale: bool = True
    is_free: bool = False


class MovieCreate(MovieBase):
    genre_ids: List[int] = []
    actor_ids: List[int] = []


class MovieUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    year: int | None = None
    rating: float | None = None
    poster_url: str | None = None
    trailer_url: str | None = None
    is_published: bool | None = None

    price: float | None = None
    currency: str | None = None
    is_for_sale: bool | None = None
    is_free: bool | None = None

    genre_ids: List[int] | None = None
    actor_ids: List[int] | None = None


class MovieRead(BaseModel):
    id: int
    title: str
    description: str | None = None
    year: int
    rating: float | None = None
    poster_url: str | None = None
    trailer_url: str | None = None
    is_published: bool = True

    price: float
    currency: str = "USD"
    is_for_sale: bool = True
    is_free: bool = False
    genres: List[GenreRead] = []
    actors: List[ActorRead] = []

    class Config:
        from_attributes = True
