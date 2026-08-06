# app/routers/control.py
from fastapi import APIRouter, Depends, HTTPException, status

from app.client import DolphinAPIError, DolphinClient
from app.dependencies import get_dolphin_client
from app.schemas import TurnOffResponse, TurnOnRequest, TurnOnResponse

router = APIRouter(prefix="/control", tags=["Device Control"])


@router.post(
    "/turn-on",
    response_model=TurnOnResponse,
    summary="Turn heater on manually",
)
async def turn_on(
    payload: TurnOnRequest,
    client: DolphinClient = Depends(get_dolphin_client),
) -> TurnOnResponse:
    """Turn on the boiler manually with a target temperature."""
    try:
        raw_response = await client.turn_on_manually(temperature=payload.temperature)
        return TurnOnResponse.model_validate(raw_response)
    except DolphinAPIError as err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Dolphin Cloud API Error: {err}",
        ) from err


@router.post(
    "/turn-off",
    response_model=TurnOffResponse,
    summary="Turn heater off manually",
)
async def turn_off(
    client: DolphinClient = Depends(get_dolphin_client),
) -> TurnOffResponse:
    """Turn off the boiler manually."""
    try:
        raw_response = await client.turn_off_manually()
        return TurnOffResponse.model_validate(raw_response)
    except DolphinAPIError as err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Dolphin Cloud API Error: {err}",
        ) from err