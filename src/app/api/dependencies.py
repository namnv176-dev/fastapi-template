from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.db.database import async_get_db
from ..core.exceptions.http_exceptions import ForbiddenException, UnauthorizedException
from ..core.logger import logging
from ..core.security import TokenType, oauth2_scheme, verify_token
from ..models.user import User

logger = logging.getLogger(__name__)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(async_get_db)]
) -> User:
    token_data = await verify_token(token, TokenType.ACCESS, db)
    if token_data is None:
        raise UnauthorizedException("User not authenticated.")

    if "@" in token_data.username_or_email:
        query = await db.execute(select(User).where(User.email == token_data.username_or_email, not User.is_deleted))
    else:
        query = await db.execute(select(User).where(User.username == token_data.username_or_email, not User.is_deleted))

    user = query.scalar_one_or_none()

    if user:
        return user

    raise UnauthorizedException("User not authenticated.")


async def get_optional_user(request: Request, db: AsyncSession = Depends(async_get_db)) -> User | None:
    token = request.headers.get("Authorization")
    if not token:
        return None

    try:
        token_type, _, token_value = token.partition(" ")
        if token_type.lower() != "bearer" or not token_value:
            return None

        token_data = await verify_token(token_value, TokenType.ACCESS, db)
        if token_data is None:
            return None

        return await get_current_user(token_value, db=db)

    except HTTPException as http_exc:
        if http_exc.status_code != 401:
            logger.error(f"Unexpected HTTPException in get_optional_user: {http_exc.detail}")
        return None

    except Exception as exc:
        logger.error(f"Unexpected error in get_optional_user: {exc}")
        return None


async def get_current_superuser(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if not current_user.is_superuser:
        raise ForbiddenException("You do not have enough privileges.")

    return current_user
