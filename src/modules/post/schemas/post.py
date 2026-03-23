from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.db.models.post import PostStatus


class TagResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class MinimalUserResponse(BaseModel):
    id: int
    username: str
    email: str
    profile_image_url: str

    model_config = ConfigDict(from_attributes=True)


class PostBase(BaseModel):
    title: str = Field(..., max_length=255)
    content: str


class PostCreate(PostBase):
    status: PostStatus = PostStatus.draft
    # Note: author_id will be set in the service, so we don't need it here


class PostUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    content: str | None = None
    status: PostStatus | None = None


class PostResponse(PostBase):
    id: int
    author_id: int
    status: PostStatus
    is_deleted: bool
    created_at: datetime
    updated_at: datetime | None = None
    published_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class CommentUpdate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: int
    post_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
