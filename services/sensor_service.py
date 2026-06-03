from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime
from models.models import SensorData, Device
from schemas.schemas import SensorDataCreate, SensorDataFilter, DeviceCreate, DeviceUpdate, DeviceSensorData
from loglib import logger




async def create_sensor_data(db: AsyncSession, data: SensorDataCreate) -> SensorData:
    """Асинхронное создание записи"""
    db_data = SensorData(**data.model_dump())
    db.add(db_data)
    await db.commit()
    await db.refresh(db_data)
    return db_data


async def get_sensor_data(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[SensorData]:
    """Асинхронное получение данных"""
    result = await db.execute(
        select(SensorData)
        .order_by(SensorData.datestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())

async def get_sensor_data_by_device( db: AsyncSession, device: str, limit: int = 100) -> List[SensorData]:
    """Получить данные по устройству"""
    result = await db.execute(
        select(SensorData).where(SensorData.device_id == device)
        .limit(limit)
    )
    
    return list(result.scalars().all())


async def get_sensor_data_filter(db: AsyncSession, filter:SensorDataFilter, limit: int =100) -> List[SensorData]:
    """Получить данные по фильтру"""
   
    query = select(SensorData)
    
    if filter.device:
        query = query.where(SensorData.device_id == filter.device)
        
    if filter.tag:
        query = query.where(SensorData.tag == filter.tag)
           
    query = query.order_by(SensorData.datestamp.desc()).limit(limit)
    result = await db.execute(query)
    
    return list(result.scalars().all())
    

async def get_sensor_data_by_device_id(db: AsyncSession, device_id: int, limit: int = 100) -> List[SensorData]:
    """Получить данные по ID устройства"""
    result = await db.execute(
        select(SensorData)
        .where(SensorData.device_id == device_id)
        .order_by(SensorData.datestamp.desc())
        .limit(limit)
    )
    
    return list(result.scalars().all())


async def get_device_sensor_data(db: AsyncSession,  limit: int = 100) -> List[DeviceSensorData]:

    """Получить данные с именем устройства (JOIN)"""
    result = await db.execute(
        select(SensorData, Device.name.label('device_name'), Device.description)
        .join(Device, SensorData.device_id == Device.id)
        .order_by(SensorData.datestamp.desc())
        .limit(limit)
    )
    
    responses = []
    for row in result:
        sensor = row.SensorData  # или row[0]

        # Создаем Pydantic модель
        response = DeviceSensorData(
            id=sensor.id,
            device_id=sensor.device_id,
            device_name=row.device_name,
            device_description=row.description,
            tag=sensor.tag,
            value=sensor.value,
            datestamp=sensor.datestamp,
            created_at=sensor.created_at
        )
        responses.append(response)

    return responses
