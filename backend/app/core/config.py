"""
AmEx Pulse — Application Configuration
=======================================
Centralized configuration using Pydantic Settings.
All environment variables are loaded here with sensible defaults for development.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "AmEx Pulse"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-Powered Cross-Channel Customer Journey Intelligence Platform"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # ── Server ───────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    # ── Database (SQLite for hackathon, PostgreSQL for production) ──
    DATABASE_URL: str = "sqlite+aiosqlite:///./amex_pulse.db"
    DATABASE_ECHO: bool = False

    # ── Redis ────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 300  # 5 minutes

    # ── Security ─────────────────────────────────────────────────
    SECRET_KEY: str = "amex-pulse-hackathon-secret-key-change-in-production-2024"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours
    BCRYPT_ROUNDS: int = 12

    # ── AI/ML ────────────────────────────────────────────────────
    AI_MODEL_DIR: str = "./models"
    INTENT_MODEL_PATH: str = "./models/intent_classifier.pkl"
    CHURN_MODEL_PATH: str = "./models/churn_predictor.pkl"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

    # ── Vector Store ─────────────────────────────────────────────
    CHROMA_PERSIST_DIR: str = "./chroma_data"

    # ── Event Simulation ─────────────────────────────────────────
    SIMULATOR_ENABLED: bool = True
    SIMULATOR_INTERVAL_MS: int = 2000  # Event every 2 seconds
    SIMULATOR_CUSTOMER_COUNT: int = 50

    # ── Rate Limiting ────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 100


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton — avoids re-reading .env on every request."""
    return Settings()
