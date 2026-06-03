from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List



class DeviceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100,
                          description="Название устройства")
    description: Optional[str] = Field(None, description="Описание устройства")
    is_active: bool = Field(True, description="Активно ли устройство")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Название устройства не может быть пустым')
        return v.strip()

class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None

class DeviceResponse(DeviceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        form_attributes = True
        


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
    device_id: int
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
    tag: Optional[str] = None
   

class DeviceSensorData(SensorDataBase):
    """Схема ответа для данных сенсора с именем устройства"""
    id: int = Field(..., description="Уникальный идентификатор записи")
    device_id: int = Field(..., description="ID устройства")
    device_name: Optional[str] = Field(None, description="Название устройства")
    device_description: Optional[str] = Field(None, description="Описание устройства")
    tag: str = Field(...,
                    description="Тег датчика (temperature, humidity и т.д.)")
    value: float = Field(..., description="Значение сенсора")
    datestamp: datetime = Field(..., description="Время измерения")
    created_at: datetime = Field(..., description="Время создания записи в БД")
    class Config:
        from_attributes = True  # Позволяет создавать из ORM объектов
