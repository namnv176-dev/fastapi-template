from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy import exc, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_superuser, get_current_user
from src.core.db.database import async_get_db
from src.core.exceptions.http_exceptions import DuplicateValueException, ForbiddenException, NotFoundException
from src.core.security import blacklist_token, get_password_hash, oauth2_scheme
from ...models.user import User
from ...schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(tags=["users"])


@router.post("/user", response_model=UserRead, status_code=201)
async def write_user(
    request: Request, user: UserCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, Any]:
    email_query = await db.execute(select(User).where(User.email == user.email, not User.is_deleted))
    if email_query.scalar_one_or_none():
        raise DuplicateValueException("Email is already registered")

    username_query = await db.execute(select(User).where(User.username == user.username, not User.is_deleted))
    if username_query.scalar_one_or_none():
        raise DuplicateValueException("Username not available")

    user_dict = user.model_dump()
    hashed_password = get_password_hash(password=user_dict["password"])

    db_user = User(
        name=user.name,
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    try:
        await db.commit()
        await db.refresh(db_user)
    except exc.SQLAlchemyError:
        await db.rollback()
        raise NotFoundException("Failed to create user")

    return db_user


@router.get("/user/me/", response_model=UserRead)
async def read_users_me(request: Request, current_user: Annotated[User, Depends(get_current_user)]) -> dict:
    return current_user


@router.get("/user/{username}", response_model=UserRead)
async def read_user(
    request: Request, username: str, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, Any]:
    query = await db.execute(select(User).where(User.username == username, not User.is_deleted))
    db_user = query.scalar_one_or_none()
    if db_user is None:
        raise NotFoundException("User not found")

    return db_user


@router.patch("/user/{username}")
async def patch_user(
    request: Request,
    values: UserUpdate,
    username: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    query = await db.execute(select(User).where(User.username == username, not User.is_deleted))
    db_user = query.scalar_one_or_none()
    if db_user is None:
        raise NotFoundException("User not found")

    if db_user.username != current_user.username:
        raise ForbiddenException("Forbidden")

    if values.email is not None and values.email != db_user.email:
        email_query = await db.execute(select(User).where(User.email == values.email))
        if email_query.scalar_one_or_none():
            raise DuplicateValueException("Email is already registered")
        db_user.email = values.email

    if values.username is not None and values.username != db_user.username:
        username_query = await db.execute(select(User).where(User.username == values.username))
        if username_query.scalar_one_or_none():
            raise DuplicateValueException("Username not available")
        db_user.username = values.username

    if values.name is not None:
        db_user.name = values.name
    if values.profile_image_url is not None:
        db_user.profile_image_url = values.profile_image_url

    await db.commit()
    return {"message": "User updated"}


@router.delete("/user/{username}")
async def erase_user(
    request: Request,
    username: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
    token: str = Depends(oauth2_scheme),
) -> dict[str, str]:
    query = await db.execute(select(User).where(User.username == username, not User.is_deleted))
    db_user = query.scalar_one_or_none()
    if not db_user:
        raise NotFoundException("User not found")

    if username != current_user.username:
        raise ForbiddenException("Forbidden")

    db_user.is_deleted = True
    await blacklist_token(token=token, db=db)
    await db.commit()
    return {"message": "User deleted"}


@router.delete("/db_user/{username}", dependencies=[Depends(get_current_superuser)])
async def erase_db_user(
    request: Request,
    username: str,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    token: str = Depends(oauth2_scheme),
) -> dict[str, str]:
    query = await db.execute(select(User).where(User.username == username))
    db_user = query.scalar_one_or_none()
    if not db_user:
        raise NotFoundException("User not found")

    await db.delete(db_user)
    await blacklist_token(token=token, db=db)
    await db.commit()
    return {"message": "User deleted from the database"}
