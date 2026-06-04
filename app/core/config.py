from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Deutsch Lernen API"
    VERSION: str = "0.1.0"

    # Database
    DATABASE_URL: str = "sqlite:///./german_app.db"

    # Auth
    SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION_very_long_random_string_here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Learning
    DEFAULT_LEVEL: str = "A1"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if not isinstance(value, str):
            return value

        value = value.strip().strip('"').strip("'")

        # Helpful recovery for a common .env typo:
        # DATABASE_URL=DATABASE_URL=sqlite:///./german_app.db
        if value.startswith("DATABASE_URL="):
            value = value.split("=", 1)[1].strip()

        # Some providers expose postgres://, while SQLAlchemy expects postgresql://.
        if value.startswith("postgres://"):
            value = "postgresql://" + value[len("postgres://"):]

        return value

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
