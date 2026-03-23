from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.repositories.base import BaseRepository
from src.db.models.user import User

class UserRepository(BaseRepository[User, None, None]):
    """
    Repository for handling User database operations.
    """
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        query = select(self.model).where(self.model.email == email, self.model.is_deleted == False)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        query = select(self.model).where(self.model.username == username, self.model.is_deleted == False)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email_or_username(self, db: AsyncSession, identifier: str) -> Optional[User]:
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
