from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.crud.cart import cart_crud
from app.schemas.cart import CartRead, CartItemRead

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/movies", response_model=CartRead)
async def get_my_cart(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    cart = await cart_crud.get_or_create_for_user(db, current_user.id)
    return cart


@router.post("/movies/{movie_id}", response_model=CartItemRead)
async def add_movie_to_cart(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await cart_crud.add_movie(db, current_user.id, movie_id)


@router.delete("/movies/{movie_id}", status_code=204)
async def remove_movie_from_cart(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await cart_crud.remove_movie(db, current_user.id, movie_id)


@router.delete("/movies", status_code=204)
async def clear_my_cart(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await cart_crud.clear_cart(db, current_user.id)
