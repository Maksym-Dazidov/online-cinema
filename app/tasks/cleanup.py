import asyncio
from celery import shared_task

from app.db.session import async_session_maker
from app.crud.activation_token import activation_token_crud
from app.crud.password_reset_token import password_reset_token_crud


@shared_task(name="app.tasks.cleanup.delete_expired_tokens")
def delete_expired_tokens():
    async def _run():
        async with async_session_maker() as db:
            a_count = await activation_token_crud.delete_expired(db)
            p_count = await password_reset_token_crud.delete_expired(db)
            return {"activation_deleted": a_count, "password_deleted": p_count}

    return asyncio.run(_run())
