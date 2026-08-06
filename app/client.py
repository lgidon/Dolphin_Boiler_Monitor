# app/client.py
from typing import Any
import httpx
from app.config import settings
from app.models import DolphinMainScreenResponse


class DolphinAPIError(Exception):
    """Custom exception for Dolphin API communication failures."""

    pass


class DolphinClient:

    def __init__(
        self,
        base_url: str = settings.dolphin_base_url,
        email: str = settings.dolphin_email,
        api_key: str = settings.dolphin_api_key,
        device_name: str = settings.dolphin_device_name,
        timeout: float = 10.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.email = email
        self.api_key = api_key
        self.device_name = device_name
        self.timeout = timeout

    def _get_auth_payload(self) -> dict:
        return {
            "deviceName": self.device_name,
            "email": self.email,
            "API_Key": self.api_key,
        }

    async def _post_command(
        self, endpoint: str, extra_params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Generic helper for sending form-encoded POST requests."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        payload = self._get_auth_payload()
        if extra_params:
            payload.update(extra_params)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Python/httpx",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, data=payload, headers=headers)
                response.raise_for_status()
                raw_json = response.json()

                if isinstance(raw_json, dict) and "Error" in raw_json:
                    raise DolphinAPIError(f"API Error Response: {raw_json['Error']}")

                return raw_json
            except (httpx.HTTPError, ValueError) as err:
                raise DolphinAPIError(
                    f"Failed to execute command on {url}: {err}"
                ) from err

    async def get_main_screen_data(self) -> DolphinMainScreenResponse:
            """Fetch current telemetry and status."""
            raw_json = await self._post_command("getMainScreenData.php")
            return DolphinMainScreenResponse.model_validate(raw_json)

    # --- Power & Control Endpoints ---

    async def turn_on_manually(self, temperature: float) -> dict[str, Any]:
        """Turn the heater on manually targeting a specific temperature.
        
        Endpoint: turnOnManually.php
        Returns: {"Success": "Done", "expectedEndTime": "HH:MM"}
        """
        return await self._post_command(
            "turnOnManually.php", {"temperature": temperature}
        )

    async def turn_off_manually(self) -> dict[str, Any]:
        """Turn the heater off manually.
        
        Endpoint: turnOffManually.php
        Returns: {"Success": "Done"}
        """
        return await self._post_command("turnOffManually.php")
        