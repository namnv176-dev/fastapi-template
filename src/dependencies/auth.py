from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.http_exceptions import ForbiddenException, UnauthorizedException
from src.core.logger import logging
from src.core.security import TokenType, oauth2_scheme, verify_token
from src.db.models.user import User
from src.db.session import async_get_db
from src.modules.user.services.user_service import user_service

logger = logging.getLogger(__name__)

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(async_get_db)]
) -> User:
    token_data = await verify_token(token, TokenType.ACCESS, db)
    if token_data is None:
        raise UnauthorizedException("User not authenticated.")

    user = await user_service.get_user_by_username(db, token_data.username_or_email)
    if not user:
        # Fallback if username_or_email is an email
        from src.repositories.user_repo import user_repo
        user = await user_repo.get_by_email_or_username(db, token_data.username_or_email)

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
    if getattr(current_user, 'is_superuser', False) is False:
        raise ForbiddenException("You do not have enough privileges.")

    return current_user
