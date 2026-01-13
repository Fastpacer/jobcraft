from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///storage/applications.sqlite"

    # Groq API
    GROQ_API_KEY: Optional[str] = None

    # SerpAPI
    SERPAPI_API_KEY: Optional[str] = None

    # LLM
    DEFAULT_LLM_MODEL: str = "llama-3.1-8b-instant"

    # Environment
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Allow extra fields in .env without error


settings = Settings()