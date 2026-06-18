from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.crud.favorite import favorite_crud
from app.crud.movie import movie_crud
from app.schemas.favorite import FavoriteRead

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.post("/movies/{movie_id}", response_model=FavoriteRead)
async def add_favorite(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    movie = await movie_crud.get(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    return await favorite_crud.add(db, current_user.id, movie_id)


@router.delete("/movies/{movie_id}", status_code=204)
async def remove_favorite(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await favorite_crud.remove(db, current_user.id, movie_id)


@router.get("/me", response_model=list[FavoriteRead])
async def get_my_favorites(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await favorite_crud.get_for_user(db, current_user.id)
