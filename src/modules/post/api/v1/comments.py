from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.user import User
from src.db.session import async_get_db
from src.dependencies.auth import get_current_user
from src.modules.post.schemas import CommentResponse, CommentUpdate
from src.modules.post.services import post_service

router = APIRouter(prefix="/comments", tags=["comments"])


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_in: CommentUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(async_get_db),
):
    """Update a comment. Only author can update."""
    return await post_service.update_comment(db, comment_id=comment_id, obj_in=comment_in, user_id=current_user.id)


@router.delete("/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: int, current_user: Annotated[User, Depends(get_current_user)], db: AsyncSession = Depends(async_get_db)
):
    """Delete a comment. Only author can delete."""
    await post_service.delete_comment(db, comment_id=comment_id, user_id=current_user.id)
