from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.crud.review import review_crud
from app.crud.movie import movie_crud
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewRead

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/movie/{movie_id}", response_model=ReviewRead)
async def create_review(
        movie_id: int,
        data: ReviewCreate,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user),
):
    movie = await movie_crud.get(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    return await review_crud.create(
        db=db,
        user_id=current_user.id,
        movie_id=movie_id,
        data=data,
    )


@router.get("/movie/{movie_id}", response_model=list[ReviewRead])
async def get_reviews_for_movie(
        movie_id: int,
        db: AsyncSession = Depends(get_db),
):
    return await review_crud.get_for_movie(db, movie_id)


@router.get("/{review_id}", response_model=ReviewRead)
async def get_review(
        review_id: int,
        db: AsyncSession = Depends(get_db),
):
    review = await review_crud.get(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.patch("/{review_id}", response_model=ReviewRead)
async def update_review(
        review_id: int,
        data: ReviewUpdate,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user),
):
    review = await review_crud.get(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your review")

    return await review_crud.update(db, review, data)


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
        review_id: int,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user),
):
    review = await review_crud.get(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your review")

    await review_crud.delete(db, review)
