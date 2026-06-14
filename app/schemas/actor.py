from pydantic import BaseModel


class ActorBase(BaseModel):
    full_name: str
    photo_url: str | None = None


class ActorCreate(ActorBase):
    pass


class ActorRead(BaseModel):
    id: int
    full_name: str
    photo_url: str | None = None

    class Config:
        from_attributes = True
