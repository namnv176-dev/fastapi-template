from typing import Any

from sqlalchemy import and_, func, not_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.post import Comment, Like, Post, PostStatus
from src.modules.post.schemas import CommentCreate, CommentUpdate, PostCreate, PostUpdate
from src.repositories.base import BaseRepository


class PostRepository(BaseRepository[Post, PostCreate, PostUpdate]):
    def __init__(self) -> None:
        super().__init__(Post)

    async def get_published_posts(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Post]:
        query = (
            select(Post)
            .where(and_(Post.status == PostStatus.published, not_(Post.is_deleted)))
            .offset(skip)
            .limit(limit)
            .order_by(Post.created_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_user_posts(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Post]:
        query = select(Post).where(Post.author_id == user_id).offset(skip).limit(limit).order_by(Post.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_active_post_by_id(self, db: AsyncSession, post_id: int) -> Post | None:
        query = select(Post).where(and_(Post.id == post_id, not_(Post.is_deleted)))
        result = await db.execute(query)
        return result.scalar_one_or_none()


class CommentRepository(BaseRepository[Comment, CommentCreate, CommentUpdate]):
    def __init__(self) -> None:
        super().__init__(Comment)

    async def get_by_post(
        self,
        db: AsyncSession,
        post_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Comment]:
        query = (
            select(Comment)
            .where(Comment.post_id == post_id)
            .offset(skip)
            .limit(limit)
            .order_by(Comment.created_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())


class LikeRepository(BaseRepository[Like, Any, Any]):
    def __init__(self) -> None:
        super().__init__(Like)

    async def get_like(self, db: AsyncSession, post_id: int, user_id: int) -> Like | None:
        query = select(Like).where(and_(Like.post_id == post_id, Like.user_id == user_id))
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def create_like(self, db: AsyncSession, post_id: int, user_id: int) -> Like:
        db_obj = Like(post_id=post_id, user_id=user_id)
        db.add(db_obj)
        await db.flush()
        return db_obj

    async def count_likes(self, db: AsyncSession, post_id: int) -> int:
        query = select(func.count(Like.id)).where(Like.post_id == post_id)
        result = await db.execute(query)
        return result.scalar_one()


post_repository = PostRepository()
comment_repository = CommentRepository()
like_repository = LikeRepository()
