from typing import Any

from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.http_exceptions import (
    DuplicateValueException,
    ForbiddenException,
    NotFoundException,
)
from src.core.security import get_password_hash, verify_password
from src.db.models.user import User
from src.repositories.user_repo import user_repo


class UserService:
    """Business logic for User module."""

    async def get_user_by_username(self, db: AsyncSession, username: str) -> User | None:
        """Fetch user profile by username."""
        return await user_repo.get_by_username(db, username)

    async def get_user_by_identifier(self, db: AsyncSession, identifier: str) -> User | None:
        """Fetch user profile by identifier (email/username)."""
        return await user_repo.get_by_identifier(db, identifier)

    async def create_user(self, db: AsyncSession, user_data: dict[str, Any]) -> User:
        """Create a new user with email and username validation."""
        # Validate existence
        if await user_repo.get_by_email(db, user_data["email"]):
            raise DuplicateValueException("Email is already registered")

        if await user_repo.get_by_username(db, user_data["username"]):
            raise DuplicateValueException("Username not available")

        # Hash and create
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
        db_user = await user_repo.create(db, obj_in=user_data)

        try:
            await db.commit()
            await db.refresh(db_user)
            return db_user
        except exc.SQLAlchemyError:
            await db.rollback()
            raise NotFoundException("Failed to create user")

    async def update_user(
        self,
        db: AsyncSession,
        username: str,
        update_data: dict[str, Any],
        current_username: str,
    ) -> dict[str, str]:
        """Update user profile with validation and permission checks."""
        user = await user_repo.get_by_username(db, username)
        if not user or user.username != current_username:
            raise ForbiddenException("Unauthorized or user not found")

        # Validate unique fields if being updated
        if "email" in update_data and update_data["email"] != user.email:
            if await user_repo.get_by_email(db, update_data["email"]):
                raise DuplicateValueException("Email is already registered")

        if "username" in update_data and update_data["username"] != user.username:
            if await user_repo.get_by_username(db, update_data["username"]):
                raise DuplicateValueException("Username not available")

        # Apply update
        await user_repo.update(db, db_obj=user, obj_in=update_data)
        await db.commit()
        return {"message": "User updated"}

    async def delete_user(
        self,
        db: AsyncSession,
        username: str,
        current_username: str,
    ) -> None:
        """Soft delete current user."""
        user = await user_repo.get_by_username(db, username)
        if not user or user.username != current_username:
            raise ForbiddenException("Unauthorized or user not found")

        await user_repo.update(db, db_obj=user, obj_in={"is_deleted": True})
        await db.commit()

    async def hard_delete_user(self, db: AsyncSession, username: str) -> None:
        """Physically remove user from DB (Admin only logic)."""
        user = await user_repo.get_by_username(db, username)
        if not user:
            raise NotFoundException("User not found")

        await db.delete(user)
        await db.commit()

    async def authenticate_user(
        self,
        db: AsyncSession,
        username_or_email: str,
        password: str,
    ) -> User | None:
        """Authenticate user against hashed credentials."""
        user = await user_repo.get_by_identifier(db, username_or_email)
        if not user or not await verify_password(password, user.hashed_password):
            return None

        return user


user_service = UserService()
