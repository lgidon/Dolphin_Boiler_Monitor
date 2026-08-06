# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    dolphin_base_url: str = "https://api.dolphinboiler.com/HA/V1"
    dolphin_email: str
    dolphin_api_key: str
    dolphin_device_name: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
