# tests/test_routers.py
import pytest
import respx
from httpx import ASGITransport, AsyncClient, Response
from app.main import app


@pytest.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@respx.mock
async def test_api_turn_on_success(async_client: AsyncClient):
    respx.post("https://api.dolphinboiler.com/HA/V1/turnOnManually.php").mock(
        return_value=Response(
            200, json={"Success": "Done", "expectedEndTime": "14:15"}
        )
    )

    response = await async_client.post("/control/turn-on", json={"temperature": 55.0})

    assert response.status_code == 200
    assert response.json() == {"Success": "Done", "expectedEndTime": "14:15"}


@respx.mock
async def test_api_turn_off_success(async_client: AsyncClient):
    respx.post("https://api.dolphinboiler.com/HA/V1/turnOffManually.php").mock(
        return_value=Response(200, json={"Success": "Done"})
    )

    response = await async_client.post("/control/turn-off")

    assert response.status_code == 200
    assert response.json() == {"Success": "Done"}


async def test_api_turn_on_validation_error(async_client: AsyncClient):
    # Temp below allowed range (30-80) should fail validation (HTTP 422)
    response = await async_client.post("/control/turn-on", json={"temperature": 15.0})
    assert response.status_code == 422