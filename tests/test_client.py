# tests/test_client.py
import pytest
import respx
from httpx import Response

from app.client import DolphinAPIError, DolphinClient
from app.models import DolphinMainScreenResponse


@respx.mock
async def test_get_main_screen_data_success():
    respx.post("https://api.dolphinboiler.com/HA/V1/getMainScreenData.php").mock(
        return_value=Response(
            200,
            json={
                "dolphinPlus": "enabled",
                "fixedTemperature": "OFF",
                "Power": "OFF",
                "Energy": 0,
                "Temperature": 46,
                "targetTemperature": None,
                "showerTemperature": [
                    {"drop": 1, "temp": 41},
                    {"drop": 2, "temp": 47},
                    {"drop": 3, "temp": 53},
                    {"drop": 4, "temp": 56},
                    {"drop": 5, "temp": 59},
                    {"drop": 6, "temp": 62},
                ],
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

    assert data.current_temp == 46
    assert data.is_heating == False
    assert data.target_temp is None


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
# -- Will be skipped by default, since it uses real credentials ---
# --- To run use: uv run pytest -m live  ---
@pytest.mark.live
async def test_live_dolphin_cloud_api():
    """Fetch real data from the live endpoint using credentials in .env."""
    client = DolphinClient()
    data = await client.get_main_screen_data()

    print("\n--- LIVE DOLPHIN API RESPONSE ---")
    print(data)
    print("---------------------------------")

    print("\n--- PARSED TELEMETRY ---")
    print(f"Current Temp: {data.current_temp} °C")
    print(f"Target Temp:  {data.target_temp} °C")
    print(f"Heating:      {data.is_heating}")
    print("------------------------")

    assert isinstance(data, DolphinMainScreenResponse)


@respx.mock
async def test_turn_on_manually():
    route = respx.post("https://api.dolphinboiler.com/HA/V1/turnOnManually.php").mock(
        return_value=Response(200, json={"Success": "Done", "expectedEndTime": "13:08"})
    )

    client = DolphinClient(
        base_url="https://api.dolphinboiler.com/HA/V1",
        email="test@example.com",
        api_key="mock-key",
        device_name="device-1",
    )

    response = await client.turn_on_manually(temperature=50.0)

    assert response["Success"] == "Done"
    assert response["expectedEndTime"] == "13:08"

    last_request = route.calls.last.request
    assert "temperature=50.0" in last_request.content.decode()


@respx.mock
async def test_turn_off_manually():
    route = respx.post("https://api.dolphinboiler.com/HA/V1/turnOffManually.php").mock(
        return_value=Response(200, json={"Success": "Done"})
    )

    client = DolphinClient(
        base_url="https://api.dolphinboiler.com/HA/V1",
        email="test@example.com",
        api_key="mock-key",
        device_name="device-1",
    )

    response = await client.turn_off_manually()

    assert response["Success"] == "Done"
    assert route.called
