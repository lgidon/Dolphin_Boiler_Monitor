import logging

from sqlalchemy.exc import SQLAlchemyError

from app.client import DolphinAPIError, DolphinClient
from app.database import AsyncSessionLocal
from app.sql_models import TelemetryLog

logger = logging.getLogger(__name__)


async def poll_heater_data(client: DolphinClient) -> None:
    """Polls the Dolphin API for status and records the snapshot to SQLite."""
    try:
        status = await client.get_main_screen_data()
        print(status)
        async with AsyncSessionLocal() as session, session.begin():
            log_entry = TelemetryLog(
                device_id=client.device_name,
                is_power_on=getattr(status, "is_heating", False),
                target_temperature=getattr(status, "target_temp", None),
                current_temperature=getattr(status, "current_temp", None),
                raw_payload=status.model_dump_json()
                if hasattr(status, "model_dump_json")
                else None,
            )
            print(log_entry)
            session.add(log_entry)

        logger.info("Successfully recorded heater telemetry snapshot.")

    except DolphinAPIError as e:
        logger.error(f"Dolphin API error during polling cycle: {e}")
    except SQLAlchemyError as e:
        logger.error(f"Database error while saving telemetry reading: {e}")
    except Exception:
        logger.exception("Unexpected error during polling cycle:")
