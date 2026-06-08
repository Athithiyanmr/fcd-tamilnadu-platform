from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # API security
    API_SECRET_KEY: str
    API_ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # TiTiler
    TITILER_URL: str = "http://titiler:8080"

    # Storage
    STORAGE_BACKEND: str = "local"  # local | s3 | gcs
    STORAGE_LOCAL_PATH: str = "/data/cogs"
    S3_BUCKET: Optional[str] = None
    GCS_BUCKET: Optional[str] = None

    # GitHub
    GITHUB_REPO: str = "Athithiyanmr/fcd-tamilnadu-platform"
    GITHUB_TOKEN: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
