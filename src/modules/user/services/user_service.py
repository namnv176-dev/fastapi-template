from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.http_exceptions import DuplicateValueException, ForbiddenException, NotFoundException
from src.core.security import get_password_hash, verify_password
from src.db.models.user import User
from src.repositories.user_repo import user_repo


class UserService:
    """
    Service layer for User entity.
    Handles all business logic and controls database transactions (commit/rollback).
    """

    async def get_user_by_username(self, db: AsyncSession, username: str) -> User | None:
        return await user_repo.get_by_username(db, username)

    async def create_user(self, db: AsyncSession, user_data: dict) -> User:
        """
        Creates a user and commits the transaction.
        """
        existing_email = await user_repo.get_by_email(db, user_data["email"])
        if existing_email:
            raise DuplicateValueException("Email is already registered")

        existing_username = await user_repo.get_by_username(db, user_data["username"])
        if existing_username:
            raise DuplicateValueException("Username not available")

        # Hash password safely
        hashed_password = get_password_hash(password=user_data["password"])

        # Pure repo call
        db_user = user_repo.create_user(
            db,
            name=user_data["name"],
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=hashed_password,
        )

        try:
            await db.commit()
            await db.refresh(db_user)
            return db_user
        except exc.SQLAlchemyError:
            await db.rollback()
            raise NotFoundException("Failed to create user")

    async def update_user(self, db: AsyncSession, username: str, update_data: dict, current_user_username: str) -> dict:
        """
        Updates a user and commits the transaction.
        """
        user = await user_repo.get_by_username(db, username)
        if not user:
            raise NotFoundException("User not found")
        if user.username != current_user_username:
            raise ForbiddenException("Forbidden")

        if "email" in update_data and update_data["email"] != user.email:
            existing_email = await user_repo.get_by_email(db, update_data["email"])
            if existing_email:
                raise DuplicateValueException("Email is already registered")
            user.email = update_data["email"]

        if "username" in update_data and update_data["username"] != user.username:
            existing_uname = await user_repo.get_by_username(db, update_data["username"])
            if existing_uname:
                raise DuplicateValueException("Username not available")
            user.username = update_data["username"]

        for k, v in update_data.items():
            if k not in ["email", "username"]:
                setattr(user, k, v)

        db.add(user)
        try:
            await db.commit()
        except exc.SQLAlchemyError:
            await db.rollback()
            raise

        return {"message": "User updated"}

    async def delete_user(self, db: AsyncSession, username: str, current_user_username: str) -> dict:
        """
        Soft deletes a user.
        """
        user = await user_repo.get_by_username(db, username)
        if not user:
            raise NotFoundException("User not found")

        if user.username != current_user_username:
            raise ForbiddenException("Forbidden")

        user.is_deleted = True
        db.add(user)
        try:
            await db.commit()
        except exc.SQLAlchemyError:
            await db.rollback()
            raise

        return {"message": "User deleted"}

    async def hard_delete_user(self, db: AsyncSession, username: str) -> dict:
        user = await user_repo.get_by_username(db, username)
        if not user:
            raise NotFoundException("User not found")

        await db.delete(user)
        try:
            await db.commit()
        except exc.SQLAlchemyError:
            await db.rollback()
            raise

        return {"message": "User deleted from the database"}

    async def authenticate_user(self, db: AsyncSession, username_or_email: str, password: str) -> User | bool:
        user = await user_repo.get_by_email_or_username(db, username_or_email)
        if not user:
            return False

        if not await verify_password(password, user.hashed_password):
            return False

        return user

user_service = UserService()
