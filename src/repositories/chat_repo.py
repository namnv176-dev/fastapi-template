from typing import Any
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.chat import ChatMessage, Conversation
from src.repositories.base import BaseRepository


class ConversationCreate(BaseModel):
    user_id: int
    title: str | None = None


class MessageCreate(BaseModel):
    conversation_id: int
    role: str
    content: str
    token_count: int | None = 0


class ConversationRepository(BaseRepository[Conversation, ConversationCreate, Any]):
    def __init__(self) -> None:
        super().__init__(Conversation)

    async def get_by_uuid(self, db: AsyncSession, uuid: UUID) -> Conversation | None:
        query = select(self.model).where(self.model.uuid == uuid)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user(self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 10) -> list[Conversation]:
        query = select(self.model).where(self.model.user_id == user_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())


class MessageRepository(BaseRepository[ChatMessage, MessageCreate, Any]):
    def __init__(self) -> None:
        super().__init__(ChatMessage)

    async def get_by_conversation(self, db: AsyncSession, conversation_id: int) -> list[ChatMessage]:
        query = select(self.model).where(self.model.conversation_id == conversation_id).order_by(self.model.created_at)
        result = await db.execute(query)
        return list(result.scalars().all())


conversation_repo = ConversationRepository()
message_repo = MessageRepository()
