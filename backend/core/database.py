"""
Database Configuration.
Creates SQLAlchemy engine, session factory, and declarative base.
All models import Base from here to register themselves.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from backend.core.config import settings

# Synchronous engine — FastAPI endpoints will use sync sessions via dependency injection.
# For high-traffic production use, replace with AsyncEngine.
# Check if using SQLite to add thread args
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,   # Verify connection before reuse
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Declarative base class for all SQLAlchemy models."""
    pass


def get_db():
    """
    FastAPI dependency that provides a DB session per request.
    Session is always closed even if an exception is raised.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_tables():
    """
    Creates all tables defined in the models.
    Call this once at application startup (used in Step 3 seeding).
    """
    from backend.models import schema  # noqa: F401 — ensures models are registered
    Base.metadata.create_all(bind=engine)
