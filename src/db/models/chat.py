from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID as UUID_PKG

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7

from src.db.session import Base

if TYPE_CHECKING:
    from src.db.models.user import User


class Conversation(Base):
    __tablename__ = "conversation"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    uuid: Mapped[UUID_PKG] = mapped_column(UUID(as_uuid=True), default_factory=uuid7, unique=True, index=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))

    user: Mapped["User"] = relationship(back_populates="conversations", init=False)
    messages: Mapped[list["ChatMessage"]] = relationship(back_populates="conversation", init=False)


class ChatMessage(Base):
    __tablename__ = "chat_message"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversation.id"), index=True)
    role: Mapped[str] = mapped_column(String(50))  # system, human, ai
    content: Mapped[str] = mapped_column(Text)
    token_count: Mapped[int | None] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))

    conversation: Mapped["Conversation"] = relationship(back_populates="messages", init=False)
