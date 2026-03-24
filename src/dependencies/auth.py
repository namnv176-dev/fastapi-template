from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.http_exceptions import ForbiddenException, UnauthorizedException
from src.core.logger import logging
from src.core.security import TokenType, oauth2_scheme, verify_token
from src.db.models.user import User
from src.db.session import async_get_db
from src.modules.user.access import get_user_info

logger = logging.getLogger(__name__)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> User:
    """Fetch the currently authenticated user from the token."""
    token_data = await verify_token(token, TokenType.ACCESS, db)
    if token_data is None:
        raise UnauthorizedException("User not authenticated.")

    # Rule: Access module's logic via access.py proxy
    user = await get_user_info(db, token_data.username_or_email)

    # Check if user was found by email fallback (if get_user_info only checked username)
    # Actually, let's keep it simple: get_user_info should handle the identifier.
    if user:
        return user

    raise UnauthorizedException("User not authenticated.")


async def get_optional_user(
    request: Request,
    db: AsyncSession = Depends(async_get_db),
) -> User | None:
    """Safely fetch user if token exists, else return None."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    try:
        token_type, _, token_value = auth_header.partition(" ")
        if token_type.lower() != "bearer" or not token_value:
            return None

        return await get_current_user(token_value, db=db)

    except HTTPException as http_exc:
        if http_exc.status_code != 401:
            logger.error(f"Unexpected HTTPException in get_optional_user: {http_exc.detail}")
        return None

    except Exception as exc:
        logger.error(f"Unexpected error in get_optional_user: {exc}")
        return None


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Ensure current user has superuser privileges."""
    if not getattr(current_user, "is_superuser", False):
        raise ForbiddenException("You do not have enough privileges.")

    return current_user
