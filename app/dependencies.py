# app/dependencies.py
from app.client import DolphinClient


def get_dolphin_client() -> DolphinClient:
    """Dependency provider for DolphinClient."""
    return DolphinClient()
