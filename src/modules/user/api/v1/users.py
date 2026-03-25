from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.http_exceptions import NotFoundException
from src.core.security import blacklist_token, oauth2_scheme
from src.db.models.user import User
from src.db.session import async_get_db
from src.dependencies.auth import get_current_superuser, get_current_user
from src.modules.user.schemas import UserCreate, UserRead, UserUpdate
from src.modules.user.services import user_service

router = APIRouter(tags=["users"])


@router.post("/user", response_model=UserRead, status_code=201)
async def write_user(request: Request, user: UserCreate, db: Annotated[AsyncSession, Depends(async_get_db)]) -> User:
    db_user = await user_service.create_user(db, user.model_dump())
    return db_user


@router.get("/user/me/", response_model=UserRead)
async def read_users_me(request: Request, current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


@router.get("/user/{username}", response_model=UserRead)
async def read_user(request: Request, username: str, db: Annotated[AsyncSession, Depends(async_get_db)]) -> User:
    db_user = await user_service.get_user_by_username(db, username)
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
    # Pass update_data without unset values
    update_data = values.model_dump(exclude_unset=True)
    return await user_service.update_user(db, username, update_data, current_user.username)


@router.delete("/user/{username}")
async def erase_user(
    request: Request,
    username: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
    token: str = Depends(oauth2_scheme),
) -> dict[str, str]:
    await user_service.delete_user(db, username, current_user.username)
    await blacklist_token(token=token, db=db)
    return {"message": "User deleted"}


@router.delete("/db_user/{username}", dependencies=[Depends(get_current_superuser)])
async def erase_db_user(
    request: Request,
    username: str,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    token: str = Depends(oauth2_scheme),
) -> dict[str, str]:
    await user_service.hard_delete_user(db, username)
    await blacklist_token(token=token, db=db)
    return {"message": "User deleted from the database"}
