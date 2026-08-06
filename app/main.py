# from fastapi import FastAPI

# app = FastAPI(
#     title="Boiler Monitor API",
#     version="0.1.0",
#     description="REST API for monitoring and controlling a network-connected water heater.",
# )


# @app.get("/")
# def root():
#     return {"service": "Boiler Monitor API", "status": "running"}

from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from app.api.routes import router
from app.config import settings
from app.db import init_db
from app.poller import poll_heater_data

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    scheduler.add_job(
        poll_heater_data,
        "interval",
        seconds=settings.polling_interval_seconds,
    )
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="Dolphin Water Heater Monitor", lifespan=lifespan)
app.include_router(router)  