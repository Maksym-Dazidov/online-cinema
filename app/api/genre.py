from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_admin, require_moderator
from app.db.session import get_db
from app.schemas.genre import GenreCreate, GenreRead
from app.crud.genre import genre_crud

router = APIRouter(prefix="/genres", tags=["Genres"])


@router.get("/", response_model=list[GenreRead])
async def get_genres(db: AsyncSession = Depends(get_db)):
    return await genre_crud.get_multi(db)


@router.get("/{genre_id}", response_model=GenreRead)
async def get_genre(genre_id: int, db: AsyncSession = Depends(get_db)):
    genre = await genre_crud.get(db, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    return genre


@router.post("/", response_model=GenreRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_moderator)])
async def create_genre(data: GenreCreate, db: AsyncSession = Depends(get_db)):
    return await genre_crud.create(db, data)


@router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_genre(genre_id: int, db: AsyncSession = Depends(get_db)):
    genre = await genre_crud.get(db, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")

    await genre_crud.delete(db, genre_id)
