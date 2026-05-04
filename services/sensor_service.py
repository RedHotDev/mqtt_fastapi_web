from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime
from models.models import SensorData
from schemas.schemas import SensorDataCreate, SensorDataFilter


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
        .order_by(SensorData.datastamp.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

