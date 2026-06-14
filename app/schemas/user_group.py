from pydantic import BaseModel

class UserGroupRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
