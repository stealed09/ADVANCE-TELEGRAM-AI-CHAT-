"""
Central configuration management using Pydantic Settings.
All values loaded from environment variables with validation.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional, List
import json


class Settings(BaseSettings):
    # ─── Telegram API ─────────────────────────────────────────────────────────
    API_ID: int = Field(..., description="Telegram API ID from my.telegram.org")
    API_HASH: str = Field(..., description="Telegram API Hash")
    PHONE_NUMBER: str = Field(..., description="Phone number with country code")
    TWO_FA_PASSWORD: Optional[str] = Field(None, description="2FA password if enabled")
    BOT_TOKEN: Optional[str] = Field(None, description="Optional bot token for admin bot")
    OWNER_ID: int = Field(..., description="Telegram user ID of the owner")
    ADMIN_IDS: str = Field("[]", description="JSON array of admin user IDs")

    # ─── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = Field(..., description="PostgreSQL connection URL")
    REDIS_URL: str = Field("redis://localhost:6379", description="Redis connection URL")

    # ─── AI / LLM ─────────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = Field(..., description="OpenAI or compatible API key")
    OPENAI_BASE_URL: str = Field(
        "https://api.openai.com/v1",
        description="API base URL (supports OpenRouter, Together, etc.)"
    )
    LLM_MODEL: str = Field("gpt-4o-mini", description="LLM model to use")
    LLM_MAX_TOKENS: int = Field(500, description="Max tokens per response")
    LLM_TEMPERATURE: float = Field(0.85, description="Response creativity (0-2)")

    # ─── Vector Store ─────────────────────────────────────────────────────────
    VECTOR_STORE_TYPE: str = Field("chroma", description="chroma or faiss")
    CHROMA_HOST: Optional[str] = Field(None, description="ChromaDB host if remote")
    EMBEDDING_MODEL: str = Field("text-embedding-3-small", description="Embedding model")

    # ─── Application ──────────────────────────────────────────────────────────
    APP_HOST: str = Field("0.0.0.0", description="FastAPI host")
    APP_PORT: int = Field(8000, description="FastAPI port")
    SECRET_KEY: str = Field(..., description="Secret key for encryption")
    ENCRYPTION_KEY: str = Field(..., description="Fernet encryption key for sessions")
    DEBUG: bool = Field(False, description="Debug mode")
    LOG_LEVEL: str = Field("INFO", description="Logging level")

    # ─── Userbot Behavior ─────────────────────────────────────────────────────
    MIN_REPLY_DELAY: float = Field(1.5, description="Minimum reply delay in seconds")
    MAX_REPLY_DELAY: float = Field(6.0, description="Maximum reply delay in seconds")
    TYPING_SPEED_CPM: int = Field(200, description="Characters per minute for typing sim")
    AUTO_REPLY_ENABLED: bool = Field(True, description="Enable auto-reply by default")
    MAX_CONTEXT_MESSAGES: int = Field(20, description="Max messages to keep in context")
    COOLDOWN_SECONDS: int = Field(3, description="Cooldown between replies to same user")

    # ─── Safety ───────────────────────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = Field(20, description="Max messages per minute")
    TOXICITY_THRESHOLD: float = Field(0.7, description="Toxicity score threshold 0-1")
    MAX_FLOOD_RETRY: int = Field(5, description="Max FloodWait retries")

    # ─── Features ─────────────────────────────────────────────────────────────
    HINGLISH_ENABLED: bool = Field(True, description="Enable Hinglish responses")
    VOICE_NOTES_ENABLED: bool = Field(False, description="Enable voice note generation")
    SENTIMENT_ANALYSIS: bool = Field(True, description="Enable sentiment analysis")
    PERSONA_NAME: str = Field("Aria", description="AI persona name")

    @validator("ADMIN_IDS", pre=True)
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            try:
                return v
            except Exception:
                return "[]"
        return v

    def get_admin_ids(self) -> List[int]:
        try:
            return json.loads(self.ADMIN_IDS)
        except Exception:
            return []

    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton instance
settings = Settings()
