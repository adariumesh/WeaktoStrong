"""
Database connection and session management with production-ready configuration
"""

import logging
from collections.abc import AsyncGenerator

from sqlalchemy.engine.events import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool, QueuePool

from app.core.config import settings
from app.models import Base

logger = logging.getLogger(__name__)

# Convert sync postgres URL to async if needed
database_url = settings.database_url
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Production-ready engine configuration
engine_kwargs = {
    "echo": settings.is_development
    and not settings.is_testing,  # Log SQL in development only
    "echo_pool": settings.debug,
    "pool_pre_ping": True,  # Enable connection health checks
    "pool_recycle": 3600,  # Recycle connections every hour
}

# Configure connection pooling based on environment
if settings.is_production:
    engine_kwargs.update(
        {
            "poolclass": QueuePool,
            "pool_size": settings.database_pool_size,
            "max_overflow": settings.database_max_overflow,
            "pool_timeout": settings.database_pool_timeout,
        }
    )
elif settings.is_testing:
    engine_kwargs.update(
        {
            "poolclass": NullPool,  # Disable pooling for tests
        }
    )
else:  # Development
    engine_kwargs.update(
        {
            "poolclass": QueuePool,
            "pool_size": 5,
            "max_overflow": 0,
            "pool_timeout": 30,
        }
    )

# Create async engine
engine = create_async_engine(database_url, **engine_kwargs)


# Add connection event listeners for monitoring
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance (if using SQLite)"""
    if "sqlite" in database_url:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()


@event.listens_for(engine.sync_engine, "checkout")
def log_connection_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log connection checkout events in debug mode"""
    if settings.debug:
        logger.debug(f"Connection checked out: {id(dbapi_connection)}")


@event.listens_for(engine.sync_engine, "checkin")
def log_connection_checkin(dbapi_connection, connection_record):
    """Log connection checkin events in debug mode"""
    if settings.debug:
        logger.debug(f"Connection checked in: {id(dbapi_connection)}")


# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,  # Disable autoflush for better control
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    Used with FastAPI dependency injection.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create all tables in the database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """Drop all tables in the database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def close_db():
    """Close database engine"""
    await engine.dispose()
