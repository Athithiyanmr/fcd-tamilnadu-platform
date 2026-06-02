from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    # API
    API_SECRET_KEY: str = "change_me"
    API_ALLOWED_ORIGINS: str = "http://localhost:3000"
    # Storage
    STORAGE_BACKEND: str = "local"  # local | s3 | gcs
    STORAGE_LOCAL_PATH: str = "/data/cogs"
    S3_BUCKET: Optional[str] = None
    GCS_BUCKET: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
