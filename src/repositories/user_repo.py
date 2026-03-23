
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.user import User
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository[User, None, None]):
    """
    Repository for handling User database operations.
    """
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        query = select(self.model).where(self.model.email == email, not self.model.is_deleted)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        query = select(self.model).where(self.model.username == username, not self.model.is_deleted)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email_or_username(self, db: AsyncSession, identifier: str) -> User | None:
        if "@" in identifier:
            return await self.get_by_email(db, identifier)
        return await self.get_by_username(db, identifier)

    def create_user(self, db: AsyncSession, **kwargs) -> User:
        """
        Creates a new user and adds it to the session.
        """
        user = User(**kwargs)
        db.add(user)
        return user

user_repo = UserRepository()
