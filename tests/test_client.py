# tests/test_client.py
import pytest
import respx
from httpx import Response
from app.client import DolphinAPIError, DolphinClient


@respx.mock
async def test_get_main_screen_data_success():
    respx.post("https://api.dolphinboiler.com/HA/V1/getMainScreenData.php").mock(
        return_value=Response(
            200,
            json={
                "status": "success",
                "temperature": 52.0,
                "is_active": 1,
            },
        )
    )

    client = DolphinClient(
        base_url="https://api.dolphinboiler.com/HA/V1",
        email="test@example.com",
        api_key="mock-key",
        device_name="device-1",
    )
    data = await client.get_main_screen_data()

    assert data["status"] == "success"
    assert data["temperature"] == 52.0


@respx.mock
async def test_get_main_screen_data_http_error():
    respx.post("https://api.dolphinboiler.com/HA/V1/getMainScreenData.php").mock(
        return_value=Response(500)
    )

    client = DolphinClient(
        base_url="https://api.dolphinboiler.com/HA/V1",
        email="test@example.com",
        api_key="mock-key",
        device_name="device-1",
    )

    with pytest.raises(DolphinAPIError):
        await client.get_main_screen_data()


# --- Live API Test: Run against production backend ---
async def test_live_dolphin_cloud_api():
    """Fetch real data from the live endpoint using credentials in .env."""
    client = DolphinClient()
    data = await client.get_main_screen_data()

    print(f"API Key = {client.api_key}")

    print("\n--- LIVE DOLPHIN API RESPONSE ---")
    print(data)
    print("---------------------------------")
    assert isinstance(data, dict)