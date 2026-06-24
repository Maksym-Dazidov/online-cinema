from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_admin, require_moderator, get_current_user
from app.crud.user_movie_access import user_movie_access_crud
from app.db.session import get_db
from app.schemas.movie import MovieCreate, MovieUpdate, MovieRead
from app.crud.movie import movie_crud
from app.crud.genre import genre_crud
from app.crud.actor import actor_crud

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("/", response_model=list[MovieRead])
async def get_movies(db: AsyncSession = Depends(get_db)):
    return await movie_crud.get_multi(db)


@router.get("/{movie_id}", response_model=MovieRead)
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    movie = await movie_crud.get(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.post("/", response_model=MovieRead, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_moderator)])
async def create_movie(data: MovieCreate, db: AsyncSession = Depends(get_db)):
    if data.genre_ids:
        for gid in data.genre_ids:
            if not await genre_crud.get(db, gid):
                raise HTTPException(status_code=400, detail=f"Genre {gid} does not exist")

    if data.actor_ids:
        for aid in data.actor_ids:
            if not await actor_crud.get(db, aid):
                raise HTTPException(status_code=400, detail=f"Actor {aid} does not exist")

    return await movie_crud.create(db, data)


@router.patch("/{movie_id}", response_model=MovieRead, dependencies=[Depends(require_moderator)])
async def update_movie(movie_id: int, data: MovieUpdate, db: AsyncSession = Depends(get_db)):
    movie = await movie_crud.get(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    if data.genre_ids is not None:
        for gid in data.genre_ids:
            if not await genre_crud.get(db, gid):
                raise HTTPException(status_code=400, detail=f"Genre {gid} does not exist")

    if data.actor_ids is not None:
        for aid in data.actor_ids:
            if not await actor_crud.get(db, aid):
                raise HTTPException(status_code=400, detail=f"Actor {aid} does not exist")

    return await movie_crud.update(db, movie, data)


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    movie = await movie_crud.get(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    await movie_crud.delete(db, movie)


@router.get("/{movie_id}/access")
async def check_movie_access(
        movie_id: int,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user),
):
    movie = await movie_crud.get(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    has_access = await user_movie_access_crud.has_access(
        db=db,
        user_id=current_user.id,
        movie_id=movie_id,
    )
    return {"access": has_access}


@router.get("/{movie_id}/stream")
async def stream_movie(
        movie_id: int,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user),
):
    movie = await movie_crud.get(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    if not movie.is_published:
        raise HTTPException(status_code=403, detail="Movie is not published")

    if movie.is_free:
        return {
            "stream_url": f"https://example.com/stream/free/{movie_id}"
        }

    has_access = await user_movie_access_crud.has_access(
        db=db,
        user_id=current_user.id,
        movie_id=movie_id,
    )

    if not has_access:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this movie",
        )

    return {
        "stream_url": f"https://example.com/stream/movie/{movie_id}"
    }
