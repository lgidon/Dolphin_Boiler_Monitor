# app/main.py
from fastapi import FastAPI

from app.routers import control

app = FastAPI(title="Dolphin Boiler Service")

app.include_router(control.router)