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




