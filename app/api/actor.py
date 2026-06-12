from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.actor import ActorCreate, ActorRead
from app.crud.actor import actor_crud

router = APIRouter(prefix="/actors", tags=["Actors"])


@router.get("/", response_model=list[ActorRead])
async def get_actors(db: AsyncSession = Depends(get_db)):
    return await actor_crud.get_multi(db)


@router.get("/{actor_id}", response_model=ActorRead)
async def get_actor(actor_id: int, db: AsyncSession = Depends(get_db)):
    actor = await actor_crud.get(db, actor_id)
    if not actor:
        raise HTTPException(status_code=404, detail="Actor not found")
    return actor


@router.post("/", response_model=ActorRead, status_code=status.HTTP_201_CREATED)
async def create_actor(data: ActorCreate, db: AsyncSession = Depends(get_db)):
    return await actor_crud.create(db, data)


@router.delete("/{actor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_actor(actor_id: int, db: AsyncSession = Depends(get_db)):
    actor = await actor_crud.get(db, actor_id)
    if not actor:
        raise HTTPException(status_code=404, detail="Actor not found")

    await actor_crud.delete(db, actor_id)
