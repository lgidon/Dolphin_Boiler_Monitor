from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
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

class DolphinMainScreenResponse(BaseModel):
    """Parses and validates telemetry from /getMainScreenData.php"""
    
    # Map raw API key names to clean Pythonic attributes if desired
    current_temp: float = Field(..., alias="Temperature")
    target_temp: float | None = Field(None, alias="targetTemperature")
    is_heating: bool = Field(..., alias="Power")
    
    # Capture local system timestamp when the response was received
    fetched_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,  # Allows instantiating with alias or field name
        arbitrary_types_allowed=True,
    )