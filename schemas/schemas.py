from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class DataItem(BaseModel):
    """Схема для элемента данных внутри MQTT сообщения"""
    datestamp: int
    tag: str
    val: float



class MQTTMessage(BaseModel):
    """Схема для входящего MQTT сообщения"""
    device: int
    data: List[DataItem]
    


class SensorDataBase(BaseModel):
    device: int
    datestamp: datetime
    tag: str 
    value: float


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
