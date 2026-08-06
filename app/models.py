from datetime import datetime
from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


# Database Model for Historical Readings
class HeaterReading(Base):
    __tablename__ = "heater_readings"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )
    current_temp: Mapped[float] = mapped_column(Float)
    target_temp: Mapped[float] = mapped_column(Float)
    state: Mapped[str] = mapped_column(String(50))


# Pydantic Schema for Response Output
class ReadingResponse(BaseModel):
    id: int
    timestamp: datetime
    current_temp: float
    target_temp: float
    state: str

    model_config = ConfigDict(from_attributes=True)