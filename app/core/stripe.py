import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(order_id: int, amount: float, user_id: int):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"Order #{order_id}"},
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1,
            }
        ],
        metadata={
            "order_id": order_id,
            "user_id": user_id,
        },
        success_url=f"{settings.FRONTEND_URL}/payment/success",
        cancel_url=f"{settings.FRONTEND_URL}/payment/cancel",
    )
    return session
