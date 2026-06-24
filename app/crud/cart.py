from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user_movie_access import user_movie_access_crud
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.movie import Movie


class CartCRUD:
    async def get_or_create_for_user(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> Cart:
        stmt = select(Cart).where(Cart.user_id == user_id)
        result = await db.execute(stmt)
        cart = result.scalar_one_or_none()

        if cart:
            return cart

        cart = Cart(user_id=user_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
        return cart

    async def get_for_user(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> Cart | None:
        stmt = select(Cart).where(Cart.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def add_movie(
        self,
        db: AsyncSession,
        user_id: int,
        movie_id: int,
    ) -> CartItem:
        cart = await self.get_or_create_for_user(db, user_id)

        movie_stmt = select(Movie).where(Movie.id == movie_id)
        movie = (await db.execute(movie_stmt)).scalar_one_or_none()
        if not movie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found",
            )

        if not movie.is_for_sale:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Movie is not available for sale",
            )

        if await user_movie_access_crud.has_access(db, user_id, movie_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Movie already purchased",
            )

        item_stmt = select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.movie_id == movie_id,
        )
        existing = (await db.execute(item_stmt)).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Movie already in cart",
            )

        item = CartItem(cart_id=cart.id, movie_id=movie_id)
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    async def remove_movie(
        self,
        db: AsyncSession,
        user_id: int,
        movie_id: int,
    ) -> None:
        cart = await self.get_for_user(db, user_id)
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found",
            )

        stmt = select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.movie_id == movie_id,
        )
        item = (await db.execute(stmt)).scalar_one_or_none()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not in cart",
            )

        await db.delete(item)
        await db.commit()

    async def clear_cart(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> None:
        cart = await self.get_for_user(db, user_id)
        if not cart:
            return

        for item in cart.items:
            await db.delete(item)

        await db.commit()


cart_crud = CartCRUD()
