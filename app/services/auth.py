from typing import Any

from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.crud.user import user_crud
from app.models.user import User


class AuthService:
    async def authenticate_user(
            self,
            db: AsyncSession,
            email: str,
            password: str,
    ) -> User | None:
        user = await user_crud.get_by_email(db, email)
        if user is None:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        return user

    async def create_tokens_for_user(self, user: User) -> dict[str, str]:
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def decode_token(self, token: str) -> dict[str, Any] | None:
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            return payload
        except JWTError:
            return None

    def get_user_id_from_token(self, token: str) -> int | None:
        payload = self.decode_token(token)
        if payload is None:
            return None

        sub = payload.get("sub")
        if sub is None:
            return None

        try:
            return int(sub)
        except (TypeError, ValueError):
            return None

    def validate_refresh_token(self, token: str) -> int | None:
        payload = self.decode_token(token)
        if payload is None:
            return None

        if payload.get("type") != "refresh":
            return None

        try:
            return int(payload.get("sub"))
        except (TypeError, ValueError):
            return None


auth_service = AuthService()
