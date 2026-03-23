from datetime import UTC, datetime
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.http_exceptions import ForbiddenException, NotFoundException
from src.db.models.post import Comment, Post, PostStatus
from src.modules.post.schemas.post import CommentCreate, CommentUpdate, PostCreate, PostUpdate
from src.repositories.post import comment_repository, like_repository, post_repository


class PostService:
    @staticmethod
    async def get_published_posts(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Post]:
        return await post_repository.get_published_posts(db, skip=skip, limit=limit)

    @staticmethod
    async def get_user_posts(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100) -> List[Post]:
        return await post_repository.get_user_posts(db, user_id=user_id, skip=skip, limit=limit)

    @staticmethod
    async def get_post_detail(db: AsyncSession, post_id: int, user_id: int | None = None) -> Post:
        post = await post_repository.get_active_post_by_id(db, post_id)
        if not post:
            raise NotFoundException("Post not found")

        if post.status != PostStatus.published:
            if user_id != post.author_id:
                raise ForbiddenException("You do not have permission to view this post")

        return post

    @staticmethod
    async def create_post(db: AsyncSession, obj_in: PostCreate, author_id: int) -> Post:
        data = obj_in.model_dump()
        data["author_id"] = author_id
        if data.get("status") == PostStatus.published:
            data["published_at"] = datetime.now(UTC)

        post = post_repository.create(db, obj_in=data)
        await db.commit()
        await db.refresh(post)
        return post

    @staticmethod
    async def update_post(db: AsyncSession, post_id: int, obj_in: PostUpdate, user_id: int) -> Post:
        post = await post_repository.get_active_post_by_id(db, post_id)
        if not post:
            raise NotFoundException("Post not found")

        if post.author_id != user_id:
            raise ForbiddenException("You can only edit your own posts")

        update_data = obj_in.model_dump(exclude_unset=True)
        # Handle status logic
        if "status" in update_data:
            if update_data["status"] == PostStatus.published and post.status != PostStatus.published:
                update_data["published_at"] = datetime.now(UTC)

        post = post_repository.update(db, db_obj=post, obj_in=update_data)
        await db.commit()
        await db.refresh(post)
        return post

    @staticmethod
    async def delete_post(db: AsyncSession, post_id: int, user_id: int) -> None:
        post = await post_repository.get_active_post_by_id(db, post_id)
        if not post:
            raise NotFoundException("Post not found")

        if post.author_id != user_id:
            raise ForbiddenException("You can only delete your own posts")

        # Soft delete
        post_repository.update(db, db_obj=post, obj_in={"is_deleted": True})
        await db.commit()

    # --- LIke System ---
    @staticmethod
    async def toggle_like(db: AsyncSession, post_id: int, user_id: int) -> dict:
        post = await post_repository.get_active_post_by_id(db, post_id)
        if not post or post.status != PostStatus.published:
            raise NotFoundException("Post not found or not published")

        existing_like = await like_repository.get_like(db, post_id=post_id, user_id=user_id)
        if existing_like:
            await like_repository.remove(db, id=existing_like.id)
            await db.commit()
            return {"detail": "Post unliked"}
        else:
            like_repository.create_like(db, post_id=post_id, user_id=user_id)
            await db.commit()
            return {"detail": "Post liked"}

    # --- Comment System ---
    @staticmethod
    async def get_comments(db: AsyncSession, post_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
        post = await post_repository.get_active_post_by_id(db, post_id)
        if not post or post.status != PostStatus.published:
            raise NotFoundException("Post not found or not published")

        return await comment_repository.get_by_post(db, post_id=post_id, skip=skip, limit=limit)

    @staticmethod
    async def create_comment(db: AsyncSession, post_id: int, obj_in: CommentCreate, user_id: int) -> Comment:
        post = await post_repository.get_active_post_by_id(db, post_id)
        if not post or post.status != PostStatus.published:
            raise NotFoundException("Post not found or not published")

        data = obj_in.model_dump()
        data["post_id"] = post_id
        data["user_id"] = user_id
        comment = comment_repository.create(db, obj_in=data)
        await db.commit()
        await db.refresh(comment)
        return comment

    @staticmethod
    async def update_comment(db: AsyncSession, comment_id: int, obj_in: CommentUpdate, user_id: int) -> Comment:
        comment = await comment_repository.get(db, id=comment_id)
        if not comment:
            raise NotFoundException("Comment not found")

        if comment.user_id != user_id:
            raise ForbiddenException("You can only edit your own comments")

        comment = comment_repository.update(db, db_obj=comment, obj_in=obj_in)
        await db.commit()
        await db.refresh(comment)
        return comment

    @staticmethod
    async def delete_comment(db: AsyncSession, comment_id: int, user_id: int) -> None:
        comment = await comment_repository.get(db, id=comment_id)
        if not comment:
            raise NotFoundException("Comment not found")

        if comment.user_id != user_id:
            raise ForbiddenException("You can only delete your own comments")

        await comment_repository.remove(db, id=comment_id)
        await db.commit()


post_service = PostService()
