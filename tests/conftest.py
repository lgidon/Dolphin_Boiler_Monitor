from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import database
from app.client import DolphinClient
from app.sql_models import Base

# In-memory SQLite database URL for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_session_factory(
    monkeypatch,
) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    """Creates an in-memory SQLite database and monkeypatches database.AsyncSessionLocal."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create tables in memory
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Build an async sessionmaker for testing
    testing_session_local = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Patch the real AsyncSessionLocal in app.database & app.poller so the poller uses in-memory DB
    monkeypatch.setattr(database, "AsyncSessionLocal", testing_session_local)
    monkeypatch.setattr("app.poller.AsyncSessionLocal", testing_session_local)

    yield testing_session_local

    # Clean up tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def mock_dolphin_client() -> AsyncMock:
    """Provides a mocked instance of DolphinClient."""
    client = AsyncMock(spec=DolphinClient)
    return client
