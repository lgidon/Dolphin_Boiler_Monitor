from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.sql_models import TelemetryLog

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])


@router.get("/current")
async def get_current_telemetry(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Fetch the latest polled boiler state."""
    result = await db.execute(
        select(TelemetryLog).order_by(TelemetryLog.timestamp.desc()).limit(1)
    )
    latest_log = result.scalars().first()

    if not latest_log:
        raise HTTPException(status_code=404, detail="No telemetry records found.")

    return latest_log


@router.get("/history")
async def get_telemetry_history(
    db: Annotated[AsyncSession, Depends(get_db)],
    hours: int = Query(
        default=24, ge=1, le=168, description="Hours of history to fetch"
    ),
    limit: int = Query(default=100, ge=1, le=1000, description="Max records to return"),
):
    """Fetch historical boiler telemetry logs for a given time window."""
    since_time = datetime.now(UTC) - timedelta(hours=hours)

    result = await db.execute(
        select(TelemetryLog)
        .where(TelemetryLog.timestamp >= since_time)
        .order_by(TelemetryLog.timestamp.asc())
        .limit(limit)
    )
    logs = result.scalars().all()

    return {
        "hours_requested": hours,
        "count": len(logs),
        "data": logs,
    }
