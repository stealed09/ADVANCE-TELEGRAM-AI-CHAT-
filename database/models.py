"""
SQLAlchemy ORM models for PostgreSQL.
All persistent data including sessions, users, conversations, memory.
"""

from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Boolean,
    DateTime, Float, JSON, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Account(Base):
    """Telegram account / userbot instance."""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False)
    session_string = Column(Text, nullable=True)  # Encrypted Telethon session
    session_data = Column(Text, nullable=True)    # Additional session metadata
    is_active = Column(Boolean, default=True)
    is_authenticated = Column(Boolean, default=False)
    owner_id = Column(BigInteger, nullable=False)
    display_name = Column(String(100), nullable=True)
    username = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_seen = Column(DateTime(timezone=True), nullable=True)
    metadata_ = Column(JSON, default={})

    conversations = relationship("Conversation", back_populates="account")
    users = relationship("UserProfile", back_populates="account")


class UserProfile(Base):
    """Profile of users who interact with the userbot."""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    telegram_id = Column(BigInteger, nullable=False)
    username = Column(String(50), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    language_code = Column(String(10), default="en")
    is_blacklisted = Column(Boolean, default=False)
    is_whitelisted = Column(Boolean, default=False)
    role = Column(String(20), default="user")  # owner/admin/moderator/user
    personality_detected = Column(String(50), nullable=True)
    preferred_language = Column(String(20), default="en")
    sentiment_trend = Column(Float, default=0.0)  # -1 to 1
    engagement_score = Column(Float, default=0.0)
    total_messages = Column(Integer, default=0)
    last_interaction = Column(DateTime(timezone=True), nullable=True)
    user_facts = Column(JSON, default={})  # Remembered facts about user
    topic_history = Column(JSON, default=[])  # Topics discussed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("account_id", "telegram_id", name="uq_account_user"),
        Index("ix_user_telegram_id", "telegram_id"),
    )

    account = relationship("Account", back_populates="users")
    conversations = relationship("Conversation", back_populates="user")


class Conversation(Base):
    """Conversation thread between userbot and a user/group."""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=True)
    chat_id = Column(BigInteger, nullable=False)
    chat_type = Column(String(20), default="private")  # private/group/channel
    is_active = Column(Boolean, default=True)
    ai_enabled = Column(Boolean, default=True)
    message_count = Column(Integer, default=0)
    quality_score = Column(Float, default=0.0)
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    context_window = Column(JSON, default=[])  # Recent message context
    metadata_ = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_conv_chat_id", "chat_id"),
        UniqueConstraint("account_id", "chat_id", name="uq_account_chat"),
    )

    account = relationship("Account", back_populates="conversations")
    user = relationship("UserProfile", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    """Individual message record."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    telegram_message_id = Column(BigInteger, nullable=True)
    role = Column(String(10), nullable=False)  # user/assistant/system
    content = Column(Text, nullable=False)
    media_type = Column(String(30), nullable=True)  # photo/video/voice/sticker
    media_description = Column(Text, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    intent_detected = Column(String(50), nullable=True)
    quality_score = Column(Float, nullable=True)
    tokens_used = Column(Integer, default=0)
    processing_time_ms = Column(Integer, default=0)
    was_edited = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_msg_conversation_id", "conversation_id"),
        Index("ix_msg_created_at", "created_at"),
    )

    conversation = relationship("Conversation", back_populates="messages")


class LongTermMemory(Base):
    """Long-term memory facts about users."""
    __tablename__ = "long_term_memory"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    telegram_id = Column(BigInteger, nullable=False)
    memory_type = Column(String(50), nullable=False)  # fact/preference/topic/emotion
    key = Column(String(200), nullable=False)
    value = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0)
    mention_count = Column(Integer, default=1)
    last_referenced = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_ltm_telegram_id", "telegram_id"),
        UniqueConstraint("account_id", "telegram_id", "key", name="uq_memory_key"),
    )


class GroupConfig(Base):
    """Configuration for group chat activation."""
    __tablename__ = "group_configs"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    group_id = Column(BigInteger, nullable=False)
    group_title = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    reply_probability = Column(Float, default=0.3)  # 30% chance to reply in groups
    trigger_keywords = Column(JSON, default=[])
    admin_only 
