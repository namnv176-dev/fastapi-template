from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.user import User
from src.modules.user.services import user_service


async def get_user_info(db: AsyncSession, identifier: str) -> User | None:
    """
    Public entry point for user module.
    Safely retrieves user by username or email.
    """
    return await user_service.get_user_by_identifier(db, identifier)
