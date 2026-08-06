# app/main.py
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.client import DolphinAPIError, DolphinClient
from app.database import init_db
from app.poller import poll_heater_data
from app.routers.control import router as control_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


async def background_polling_loop(interval_seconds: float = 10.0):
    client = DolphinClient()
    while True:
        try:
            await poll_heater_data(client)
            await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            break
        except DolphinAPIError as e:
            # Handle expected network/API failures without blowing up the loop
            logger.warning(f"Transient API error during polling: {e}")
            await asyncio.sleep(5.0)
        except Exception:
            # Fallback for unexpected failures: log the full stack trace
            logger.exception("Unexpected exception in background polling loop")
            await asyncio.sleep(5.0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize SQLite DB tables on startup
    await init_db()

    # 2. Start background worker
    polling_task = asyncio.create_task(background_polling_loop(interval_seconds=10.0))

    yield

    # 3. Clean up on shutdown
    polling_task.cancel()
    try:
        await polling_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="Dolphin Boiler Monitor API", lifespan=lifespan)

app.include_router(control_router)
