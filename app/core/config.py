from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    PROJECT_NAME: str = "Deutsch Lernen API"
    VERSION: str = "0.1.0"

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/deutsch"

    # Auth
    SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION_very_long_random_string_here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Learning
    DEFAULT_LEVEL: str = "A1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
