# app/client.py
import httpx
from app.config import settings


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

    async def get_main_screen_data(self) -> dict:
        url = f"{self.base_url}/getMainScreenData.php"
        payload = self._get_auth_payload()

        # Added standard User-Agent header
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Python/httpx",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Use data= (form-encoded) instead of json=
                response = await client.post(url, data=payload, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as err:
                raise DolphinAPIError(
                    f"Failed to fetch main screen data from {url}: {err}"
                ) from err