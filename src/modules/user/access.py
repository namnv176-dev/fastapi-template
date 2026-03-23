from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.user import User
from src.modules.user.services.user_service import user_service


async def get_user_info(db: AsyncSession, username: str) -> User | None:
    """
    Access layer for user module. Safe proxy to access user logic from other modules.
    """
    return await user_service.get_user_by_username(db, username)
