from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.payment import Payment, PaymentStatus
from app.models.payment_item import PaymentItem


class PaymentCRUD:
    async def create_for_order(
            self,
            db: AsyncSession,
            user_id: int,
            order_id: int,
    ) -> Payment:
        stmt = select(Order).where(
            Order.id == order_id,
            Order.user_id == user_id,
        )
        order = (await db.execute(stmt)).scalar_one_or_none()

        if not order:
            raise HTTPException(404, "Order not found")

        if order.status != OrderStatus.PENDING.value:
            raise HTTPException(400, "Only pending orders can be paid")

        items_stmt = select(OrderItem).where(OrderItem.order_id == order.id)
        order_items = (await db.execute(items_stmt)).scalars().all()

        if not order_items:
            raise HTTPException(400, "Order has no items")

        total = Decimal("0.00")
        for oi in order_items:
            total += Decimal(str(oi.price_at_order))

        payment = Payment(
            order_id=order.id,
            user_id=user_id,
            status=PaymentStatus.PENDING.value,
            amount=total,
            currency="USD",
        )
        db.add(payment)
        await db.flush()

        for oi in order_items:
            db.add(
                PaymentItem(
                    payment_id=payment.id,
                    order_item_id=oi.id,
                    amount=oi.price_at_order,
                )
            )

        await db.commit()
        await db.refresh(payment)
        return payment

    async def get_for_user(
            self,
            db: AsyncSession,
            user_id: int,
    ) -> list[Payment]:
        stmt = select(Payment).where(Payment.user_id == user_id).order_by(Payment.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()

    async def mark_success_by_order(
            self,
            db: AsyncSession,
            order_id: int,
            user_id: int,
    ) -> Payment:
        stmt = select(Payment).where(
            Payment.order_id == order_id,
            Payment.user_id == user_id,
        )
        payment = (await db.execute(stmt)).scalar_one_or_none()

        if not payment:
            raise HTTPException(404, "Payment not found")

        if payment.status != PaymentStatus.PENDING.value:
            return payment

        payment.status = PaymentStatus.SUCCESS.value

        order_stmt = select(Order).where(Order.id == order_id)
        order = (await db.execute(order_stmt)).scalar_one_or_none()
        if order and order.status == OrderStatus.PENDING.value:
            order.status = OrderStatus.PAID.value

        await db.commit()
        await db.refresh(payment)
        return payment


payment_crud = PaymentCRUD()
