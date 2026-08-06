from sqlalchemy.exc import SQLAlchemyError

from app.client import DolphinAPIError, DolphinClient
from app.db import AsyncSessionLocal
from app.models import HeaterReading


async def poll_heater_data():
    client = DolphinClient()
    try:
        raw_data = await client.get_status()
        async with AsyncSessionLocal() as session:
            reading = HeaterReading(
                current_temp=raw_data.get("current_temp"),
                target_temp=raw_data.get("target_temp"),
                state=raw_data.get("state", "unknown"),
            )
            session.add(reading)
            await session.commit()
    except (DolphinAPIError, SQLAlchemyError) as e:
        # Add structured logging here
        print(f"Error polling Dolphin heater: {e}")