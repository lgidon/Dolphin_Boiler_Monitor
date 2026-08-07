# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    dolphin_base_url: str = "https://api.dolphinboiler.com/HA/V1"
    dolphin_email: str
    dolphin_api_key: str
    dolphin_device_name: str

    POLL_INTERVAL_SECONDS: float = 120.0  # Default fallback if not set in .env
    TESTING: bool = False  # Flag to prevent polling during docker testing

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
