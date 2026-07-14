from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db import base
from app.db.session import async_session_maker
from app.core.config import settings
from app.crud.user import user_crud
from app.crud.user_group import user_group_crud

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.actor import router as actor_router
from app.api.genre import router as genre_router
from app.api.movie import router as movie_router
from app.api.admin import router as admin_router
from app.api.review import router as review_router
from app.api.favorite import router as favorite_router
from app.api.cart import router as cart_router
from app.api.order import router as order_router
from app.api.payment import router as payment_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_session_maker() as db:
        await user_group_crud.create_default_groups(db)
        if settings.INITIAL_ADMIN_EMAIL and settings.INITIAL_ADMIN_PASSWORD:
            await user_crud.create_initial_admin_if_absent(
                db,
                settings.INITIAL_ADMIN_EMAIL,
                settings.INITIAL_ADMIN_PASSWORD,
            )

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(actor_router)
app.include_router(genre_router)
app.include_router(movie_router)
app.include_router(admin_router)
app.include_router(review_router)
app.include_router(favorite_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(payment_router)


@app.get("/health")
def health():
    return {"status": "ok"}
