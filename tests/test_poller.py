from unittest.mock import AsyncMock, MagicMock

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.client import DolphinAPIError
from app.models import DolphinMainScreenResponse
from app.poller import poll_heater_data
from app.sql_models import TelemetryLog


async def test_poll_heater_data_success(
    mock_dolphin_client: AsyncMock,
    test_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Test that poll_heater_data fetches API data and inserts a TelemetryLog record."""
    # 1. Arrange: Mock response object
    mock_response = MagicMock(spec=DolphinMainScreenResponse)
    mock_response.is_heating = True
    mock_response.current_temp = 42.5
    mock_response.target_temp = 60.0
    mock_response.model_dump_json.return_value = '{"is_heating": true}'

    mock_dolphin_client.device_name = "test_device"
    mock_dolphin_client.get_main_screen_data.return_value = mock_response

    # 2. Act
    await poll_heater_data(mock_dolphin_client)

    # 3. Assert: Query TelemetryLog from SQLite
    async with test_session_factory() as session:
        result = await session.execute(select(TelemetryLog))
        logs = result.scalars().all()

        assert len(logs) == 1
        record = logs[0]
        assert record.device_id == "test_device"
        assert record.is_power_on is True
        assert record.current_temperature == 42.5
        assert record.target_temperature == 60.0

    mock_dolphin_client.get_main_screen_data.assert_called_once()


async def test_poll_heater_data_api_error_handling(
    mock_dolphin_client: AsyncMock,
    test_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Test that DolphinAPIError is caught cleanly and no record is saved."""
    mock_dolphin_client.get_main_screen_data.side_effect = DolphinAPIError(
        "Connection timeout"
    )

    await poll_heater_data(mock_dolphin_client)

    async with test_session_factory() as session:
        result = await session.execute(select(TelemetryLog))
        logs = result.scalars().all()

        assert len(logs) == 0
