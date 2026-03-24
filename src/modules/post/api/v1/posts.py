from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.user import User
from src.db.session import async_get_db
from src.dependencies.auth import get_current_user, get_optional_user
from src.modules.post.schemas import CommentCreate, CommentResponse, PostCreate, PostResponse, PostUpdate
from src.modules.post.services import post_service

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=PostResponse, status_code=201)
async def create_post(
    post_in: PostCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(async_get_db),
):
    """Create a new post."""
    return await post_service.create_post(db, obj_in=post_in, author_id=current_user.id)


@router.get("", response_model=list[PostResponse])
async def list_published_posts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(async_get_db)):
    """List all published and non-deleted posts."""
    return await post_service.get_published_posts(db, skip=skip, limit=limit)


@router.get("/me", response_model=list[PostResponse])
async def get_my_posts(
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(async_get_db),
):
    """List all posts (including drafts) for the current user."""
    return await post_service.get_user_posts(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post_detail(
    post_id: int, user: Annotated[User | None, Depends(get_optional_user)], db: AsyncSession = Depends(async_get_db)
):
    """Get post detail. Published posts are visible to all, draft/archived only to the author."""
    user_id = user.id if user else None
    return await post_service.get_post_detail(db, post_id=post_id, user_id=user_id)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_in: PostUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(async_get_db),
):
    """Update a post. Only the author can update."""
    return await post_service.update_post(db, post_id=post_id, obj_in=post_in, user_id=current_user.id)


@router.delete("/{post_id}", status_code=204)
async def delete_post(
    post_id: int, current_user: Annotated[User, Depends(get_current_user)], db: AsyncSession = Depends(async_get_db)
):
    """Soft delete a post. Only the author can delete."""
    await post_service.delete_post(db, post_id=post_id, user_id=current_user.id)


@router.post("/{post_id}/like", status_code=200)
async def toggle_like(
    post_id: int, current_user: Annotated[User, Depends(get_current_user)], db: AsyncSession = Depends(async_get_db)
):
    """Like or unlike a published post."""
    return await post_service.toggle_like(db, post_id=post_id, user_id=current_user.id)


@router.get("/{post_id}/comments", response_model=list[CommentResponse])
async def get_comments(post_id: int, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(async_get_db)):
    """List comments for a published post."""
    return await post_service.get_comments(db, post_id=post_id, skip=skip, limit=limit)


@router.post("/{post_id}/comments", response_model=CommentResponse, status_code=201)
async def create_comment(
    post_id: int,
    comment_in: CommentCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(async_get_db),
):
    """Create a comment on a published post."""
    return await post_service.create_comment(db, post_id=post_id, obj_in=comment_in, user_id=current_user.id)
