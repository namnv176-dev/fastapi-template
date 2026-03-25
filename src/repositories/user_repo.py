from sqlalchemy import not_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.user import User
from src.modules.user.schemas import UserCreate, UserUpdate
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """
    Repository for User operations.
    Handles low-level data access and filtering.
    """

    def __init__(self) -> None:
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        """Fetch user by email if not deleted."""
        query = select(self.model).where(self.model.email == email, not_(self.model.is_deleted))
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        """Fetch user by username if not deleted."""
        query = select(self.model).where(self.model.username == username, not_(self.model.is_deleted))
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_identifier(self, db: AsyncSession, identifier: str) -> User | None:
        """Fetch user by identifier (either email or username)."""
        query = select(self.model).where(
            or_(self.model.email == identifier, self.model.username == identifier),
            not_(self.model.is_deleted),
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()


user_repo = UserRepository()
