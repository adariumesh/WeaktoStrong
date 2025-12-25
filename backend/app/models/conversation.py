"""
SQLAlchemy models for AI conversations and messages
"""

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .user import Base


class Conversation(Base):
    """AI conversation model"""

    __tablename__ = "conversations"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    challenge_id = Column(
        UUID(as_uuid=True), nullable=True
    )  # Optional link to challenge
    title = Column(String(200), nullable=False)
    model_tier = Column(String(20), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "ConversationMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "model_tier IN ('local', 'haiku', 'sonnet')", name="valid_model_tier"
        ),
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}', tier='{self.model_tier}')>"

    @property
    def total_tokens_used(self) -> int:
        """Calculate total tokens used in this conversation"""
        return sum(
            message.tokens_used for message in self.messages if message.tokens_used
        )

    @property
    def message_count(self) -> int:
        """Get total number of messages in this conversation"""
        return len(self.messages)

    @property
    def last_message_at(self) -> datetime:
        """Get timestamp of the last message"""
        if self.messages:
            return max(message.created_at for message in self.messages)
        return self.created_at


class ConversationMessage(Base):
    """Individual message in an AI conversation"""

    __tablename__ = "conversation_messages"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    tokens_used = Column(Integer, default=0, nullable=False)
    model_used = Column(
        String(50), nullable=True
    )  # Which AI model generated this message
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant', 'system')", name="valid_message_role"
        ),
    )

    def __repr__(self):
        return f"<ConversationMessage(id={self.id}, role='{self.role}', conversation_id={self.conversation_id})>"

    @property
    def content_preview(self) -> str:
        """Get a short preview of the message content"""
        if len(self.content) <= 100:
            return self.content
        return self.content[:97] + "..."

    @property
    def is_from_user(self) -> bool:
        """Check if this message is from a user"""
        return self.role == "user"

    @property
    def is_from_ai(self) -> bool:
        """Check if this message is from an AI assistant"""
        return self.role == "assistant"
