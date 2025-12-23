"""
Pytest configuration and shared fixtures
"""

import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import Settings
from app.core.database import get_db
from app.models.base import Base
from main import app

# Test database URL (in-memory SQLite for speed)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db_engine():
    """Create a test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
        },
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session"""
    async_session = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client with dependency overrides"""

    def get_test_db():
        return test_db_session

    app.dependency_overrides[get_db] = get_test_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings"""
    return Settings(
        environment="testing",
        jwt_secret_key="test-secret-key-change-in-production",
        database_url=TEST_DATABASE_URL,
        redis_url="redis://localhost:6379/1",  # Test Redis DB
        claude_api_key="test-claude-key",
        free_tier_daily_tokens=1000,
        pro_tier_daily_tokens=10000,
    )


@pytest.fixture
def mock_redis(mocker):
    """Mock Redis for tests that don't need actual Redis"""
    mock_redis = mocker.MagicMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = True
    mock_redis.incr.return_value = 1
    mock_redis.expire.return_value = True
    return mock_redis


# Test data fixtures
@pytest.fixture
def test_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "is_active": True,
    }


@pytest.fixture
def test_ai_request_data():
    """Sample AI request data for testing"""
    return {
        "prompt": "I think the approach should be to use a loop because it's more efficient",
        "preferred_tier": "local",
        "temperature": 0.7,
        "max_tokens": 1000,
        "enforce_validation": True,
        "challenge_context": {
            "title": "Test Challenge",
            "difficulty": "beginner",
            "language": "javascript",
        },
    }


@pytest.fixture
def test_challenge_data():
    """Sample challenge data for testing"""
    return {
        "id": "test-challenge-1",
        "title": "Test Challenge",
        "description": "A test challenge for unit testing",
        "track": "web",
        "difficulty": "beginner",
        "points": 100,
        "requirements": ["Create a function", "Handle edge cases"],
        "starter_code": "// Write your code here",
        "test_config": {"type": "jest", "test_file": "test.js"},
    }
