# app/schemas.py
from pydantic import BaseModel, Field


class TurnOnRequest(BaseModel):
    temperature: float = Field(
        ...,
        ge=30.0,
        le=80.0,
        description="Target temperature in Celsius",
        examples=[50.0],
    )


class TurnOnResponse(BaseModel):
    Success: str
    expectedEndTime: str | None = None


class TurnOffResponse(BaseModel):
    Success: str
