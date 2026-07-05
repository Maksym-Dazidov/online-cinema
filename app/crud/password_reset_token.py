import secrets
from datetime import datetime, UTC

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.password_reset_token import PasswordResetToken
from app.core.security import hash_token


class PasswordResetTokenCRUD:

    async def create_or_replace(self, db: AsyncSession, user_id: int) -> tuple[PasswordResetToken, str]:
        raw = secrets.token_urlsafe(48)
        token_hash = hash_token(raw)

        stmt = select(PasswordResetToken).where(PasswordResetToken.user_id == user_id)
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            await db.delete(existing)
            await db.flush()

        token = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=PasswordResetToken.generate_expiration(),
        )
        db.add(token)
        await db.commit()
        await db.refresh(token)
        return token, raw

    async def get_by_token(self, db: AsyncSession, token: str) -> PasswordResetToken | None:
        token_hash = hash_token(token)
        stmt = select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
        return (await db.execute(stmt)).scalar_one_or_none()

    async def delete(self, db: AsyncSession, token_obj: PasswordResetToken) -> None:
        await db.delete(token_obj)
        await db.commit()

    async def delete_expired(self, db: AsyncSession) -> int:
        now = datetime.now(UTC)
        stmt = delete(PasswordResetToken).where(PasswordResetToken.expires_at < now)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount or 0


password_reset_token_crud = PasswordResetTokenCRUD()
