from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.sql_models import TelemetryLog

# Use an in-memory SQLite database for fast isolated tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


# Override the app dependency so tests hit the in-memory SQLite DB
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_get_current_telemetry_not_found(async_client: AsyncClient):
    response = await async_client.get("/telemetry/current")
    assert response.status_code == 404
    assert response.json() == {"detail": "No telemetry records found."}


@pytest.mark.asyncio
async def test_get_current_telemetry_success(async_client: AsyncClient):
    # Seed a record directly into the test database
    async with TestSessionLocal() as session:
        log = TelemetryLog(
            timestamp=datetime.now(UTC),
            device_id="TEST_DEVICE",
            is_power_on=True,
            target_temperature=60.0,
            current_temperature=45.0,
            raw_payload='{"status": "ok"}',
        )
        session.add(log)
        await session.commit()

    response = await async_client.get("/telemetry/current")
    assert response.status_code == 200
    data = response.json()
    assert data["device_id"] == "TEST_DEVICE"
    assert data["is_power_on"] is True
    assert data["current_temperature"] == 45.0


@pytest.mark.asyncio
async def test_get_telemetry_history(async_client: AsyncClient):
    # Seed historical records
    async with TestSessionLocal() as session:
        session.add(
            TelemetryLog(
                timestamp=datetime.now(UTC),
                device_id="TEST_DEVICE",
                is_power_on=False,
                target_temperature=None,
                current_temperature=30.0,
                raw_payload="{}",
            )
        )
        await session.commit()

    response = await async_client.get("/telemetry/history?hours=24&limit=10")
    assert response.status_code == 200
    body = response.json()
    assert body["hours_requested"] == 24
    assert body["count"] == 1
    assert len(body["data"]) == 1
