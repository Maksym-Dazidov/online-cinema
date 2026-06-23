from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
import stripe

from app.core.deps import get_current_user
from app.crud.user_movie_access import user_movie_access_crud
from app.db.session import get_db
from app.crud.payment import payment_crud
from app.crud.order import order_crud
from app.schemas.payment import PaymentRead
from app.core.stripe import create_checkout_session
from app.core.config import settings
from app.models.order import OrderStatus

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/orders/{order_id}", response_model=PaymentRead)
async def create_payment_for_order(
        order_id: int,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user),
):
    return await payment_crud.create_for_order(db, current_user.id, order_id)


@router.get("", response_model=list[PaymentRead])
async def list_my_payments(
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user),
):
    return await payment_crud.get_for_user(db, current_user.id)


@router.post("/stripe/create-session/{order_id}")
async def create_stripe_session(
        order_id: int,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user),
):
    order = await order_crud.get_by_id_for_user(db, current_user.id, order_id)
    if not order:
        raise HTTPException(404, "Order not found")

    if order.status != OrderStatus.PENDING.value:
        raise HTTPException(400, "Order already processed")

    if order.total_amount is None:
        raise HTTPException(400, "Order has no total amount")

    session = create_checkout_session(order.id, float(order.total_amount), current_user.id)
    return {"checkout_url": session.url}


@router.post("/stripe/webhook")
async def stripe_webhook(
        request: Request,
        db: AsyncSession = Depends(get_db),
):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except Exception:
        raise HTTPException(400, "Invalid signature")

    if event["type"] == "checkout.session.completed":
        data = event["data"]["object"]
        order_id = int(data["metadata"]["order_id"])
        user_id = int(data["metadata"]["user_id"])

        await payment_crud.mark_success_by_order(
            db,
            order_id=order_id,
            user_id=user_id,
        )

        await user_movie_access_crud.grant_for_order(
            db=db,
            user_id=user_id,
            order_id=order_id,
            payment_id=None,
        )

    return {"status": "ok"}
