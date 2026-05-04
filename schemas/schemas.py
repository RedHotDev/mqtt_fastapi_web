from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SensorDataBase(BaseModel):
    datastamp: datetime
    device: int
    temp: float = Field(..., ge=-50, le=100,
                        description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100,
                            description="Humidity in percent")


class SensorDataCreate(SensorDataBase):
    pass


class SensorDataResponse(SensorDataBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SensorDataFilter(BaseModel):
    device: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_temp: Optional[float] = None
    max_temp: Optional[float] = None
