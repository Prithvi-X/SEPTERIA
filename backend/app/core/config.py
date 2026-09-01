import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "SEPTERIA API"
    APP_ENV: str = "development"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SEPTERIA (SIH26186)"

    # Server configuration
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = int(os.getenv("PORT", os.getenv("BACKEND_PORT", "8000")))

    # PostgreSQL Database Connection
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://septeria_user:septeria_secret@localhost:5432/septeria_db"
    )

    # JWT Authentication
    JWT_SECRET: str = os.getenv(
        "JWT_SECRET",
        "septeria_sih26186_super_secure_jwt_secret_dev_key_2026"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 480

    # CORS Origins (Allow all local Next.js and Flutter Web developer ports + cloud domains)
    CORS_ORIGINS: Union[str, List[str]] = os.getenv(
        "CORS_ORIGINS",
        (
            "http://localhost:3000,http://127.0.0.1:3000,"
            "http://localhost:3001,http://127.0.0.1:3001,"
            "http://localhost:8080,http://127.0.0.1:8080,"
            "http://localhost:5000,http://127.0.0.1:5000,"
            "http://localhost:5173,http://127.0.0.1:5173"
        )
    )

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
