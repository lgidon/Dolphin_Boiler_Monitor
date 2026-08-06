from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        index=True,
    )

    # Device State Data
    device_id: Mapped[str] = mapped_column(String(50), index=True)
    is_power_on: Mapped[bool]
    target_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Optional raw JSON payload backup
    raw_payload: Mapped[str | None] = mapped_column(String, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<TelemetryLog id={self.id} device_id='{self.device_id}' "
            f"power={self.is_power_on} temp={self.current_temperature}"
            f"target_temperature={self.target_temperature}>"
        )
