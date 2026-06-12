from pydantic import BaseModel


class GenreBase(BaseModel):
    name: str


class GenreCreate(GenreBase):
    pass


class GenreRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
