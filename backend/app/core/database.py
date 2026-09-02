import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.app.core.config import settings
from backend.app.core.logging import logger

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SQLITE_DB_PATH = os.path.join(ROOT_DIR, "septeria.db")
SQLITE_FALLBACK_URL = f"sqlite:///{SQLITE_DB_PATH}"

sync_db_url = settings.DATABASE_URL
if sync_db_url.startswith("postgresql+asyncpg://"):
    sync_db_url = sync_db_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
elif sync_db_url.startswith("postgresql://"):
    sync_db_url = sync_db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

if sync_db_url.startswith("sqlite"):
    engine = create_engine(sync_db_url, connect_args={"check_same_thread": False})
else:
    try:
        engine = create_engine(
            sync_db_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )
        with engine.connect() as conn:
            pass
        logger.info("Connected to PostgreSQL database successfully.")
    except Exception as e:
        if settings.APP_ENV == "production":
            logger.error(f"FATAL: PostgreSQL connection failed in production ({e}). Crashing container to allow orchestrator restart.")
            raise e
        logger.warning(f"PostgreSQL connection failed ({e}). Falling back to local SQLite database at {SQLITE_DB_PATH}.")
        sync_db_url = SQLITE_FALLBACK_URL
        engine = create_engine(sync_db_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
