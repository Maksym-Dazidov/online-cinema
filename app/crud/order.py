from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user_movie_access import user_movie_access_crud
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.cart import Cart
from app.models.movie import Movie


class OrderCRUD:
    async def get_for_user(
            self,
            db: AsyncSession,
            user_id: int,
    ) -> list[Order]:
        stmt = select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_id_for_user(
            self,
            db: AsyncSession,
            user_id: int,
            order_id: int,
    ) -> Order | None:
        stmt = select(Order).where(
            Order.id == order_id,
            Order.user_id == user_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_from_cart(
            self,
            db: AsyncSession,
            user_id: int,
    ) -> Order:
        cart_stmt = select(Cart).where(Cart.user_id == user_id)
        cart = (await db.execute(cart_stmt)).scalar_one_or_none()

        if not cart or not cart.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty",
            )

        for item in cart.items:
            if await user_movie_access_crud.has_access(db, user_id, item.movie_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Movie №{item.movie_id} already purchased",
                )

        movie_ids = [item.movie_id for item in cart.items]
        movies_stmt = select(Movie).where(Movie.id.in_(movie_ids))
        movies = (await db.execute(movies_stmt)).scalars().all()
        movies_by_id = {m.id: m for m in movies}

        order_items: list[OrderItem] = []
        total = Decimal("0.00")

        for item in cart.items:
            movie = movies_by_id.get(item.movie_id)
            if not movie:
                continue

            if not movie.is_for_sale:
                continue

            price = Decimal(str(movie.price))
            total += price

            order_items.append(
                OrderItem(
                    movie_id=movie.id,
                    price_at_order=price,
                )
            )

        if not order_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No available movies to order",
            )

        order = Order(
            user_id=user_id,
            status=OrderStatus.PENDING.value,
            total_amount=total,
        )
        db.add(order)
        await db.flush()

        for oi in order_items:
            oi.order_id = order.id
            db.add(oi)

        for item in list(cart.items):
            await db.delete(item)

        await db.commit()
        await db.refresh(order)
        return order

    async def cancel(
            self,
            db: AsyncSession,
            user_id: int,
            order_id: int,
    ) -> Order:
        order = await self.get_by_id_for_user(db, user_id, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )

        if order.status != OrderStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending orders can be canceled",
            )

        order.status = OrderStatus.CANCELED.value
        await db.commit()
        await db.refresh(order)
        return order


order_crud = OrderCRUD()
