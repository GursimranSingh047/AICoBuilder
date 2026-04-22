from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from typing import Generator
from loguru import logger

from app.core.config import settings

# SQLite needs check_same_thread=False; ignored by other drivers
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,          # SQL query logging in debug mode
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency – yields a DB session and closes it when done."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Create all tables on startup (dev-friendly; use Alembic in prod)."""
    from app.models import user, project  # noqa: F401 – import side-effects
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created / verified.")
