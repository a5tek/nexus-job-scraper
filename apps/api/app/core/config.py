import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "Nexus"
    APP_ENV: str = "development"
    DEBUG: bool = True
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    # Database
    # Default to sqlite async for instant offline testing if no live postgres is provided
    DATABASE_URL: str = "sqlite+aiosqlite:///./nexus.db"
    SYNC_DATABASE_URL: str = "sqlite:///./nexus.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security & Auth
    SECRET_KEY: str = "nexus_super_secret_dev_key_change_in_production_32chars!"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # LLM (Gemini)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Embeddings
    EMBEDDING_PROVIDER: str = "local"
    LOCAL_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Storage
    STORAGE_PROVIDER: str = "local"
    STORAGE_LOCAL_DIR: str = "./storage/resumes"

    # Media
    HEYGEN_API_KEY: str = ""
    DID_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""

    # Processing & Cache Versions
    EXTRACTOR_VERSION: str = "1.0.0"
    EMBEDDING_VERSION: str = "1.0.0"
    MATCH_EXPLANATION_VERSION: str = "1.0.0"
    BRIEFING_PROMPT_VERSION: str = "1.0.0"

    # Sentry
    SENTRY_DSN: str = ""

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000", "http://127.0.0.1:3000"]


settings = Settings()
