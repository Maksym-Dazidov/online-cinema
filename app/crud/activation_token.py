import secrets
from datetime import datetime, UTC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activation_token import ActivationToken


class ActivationTokenCRUD:

    async def create_or_replace(self, db: AsyncSession, user_id: int) -> ActivationToken:
        stmt = select(ActivationToken).where(ActivationToken.user_id == user_id)
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            await db.delete(existing)
            await db.flush()

        token = ActivationToken(
            user_id=user_id,
            token=secrets.token_urlsafe(32),
            expires_at=ActivationToken.generate_expiration(),
        )
        db.add(token)
        await db.commit()
        await db.refresh(token)
        return token

    async def get_by_token(self, db: AsyncSession, token: str) -> ActivationToken | None:
        stmt = select(ActivationToken).where(ActivationToken.token == token)
        return (await db.execute(stmt)).scalar_one_or_none()

    async def delete(self, db: AsyncSession, token_obj: ActivationToken) -> None:
        await db.delete(token_obj)
        await db.commit()

    async def delete_expired(self, db: AsyncSession) -> int:
        now = datetime.now(UTC)
        stmt = select(ActivationToken).where(ActivationToken.expires_at < now)
        tokens = (await db.execute(stmt)).scalars().all()

        for t in tokens:
            await db.delete(t)

        await db.commit()
        return len(tokens)


activation_token_crud = ActivationTokenCRUD()
