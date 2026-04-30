from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime
from models.models import SensorData
from schemas.schemas import SensorDataCreate, SensorDataFilter


async def create_sensor_data(db: AsyncSession, data: SensorDataCreate) -> SensorData:
    db_data = SensorData(**data.model_dump())
    db.add(db_data)
    await db.commit()
    await db.refresh(db_data)
    return db_data



    from sqlalchemy import func

    query = select(
        func.avg(SensorData.temp).label("avg_temp"),
        func.min(SensorData.temp).label("min_temp"),
        func.max(SensorData.temp).label("max_temp"),
        func.avg(SensorData.humidity).label("avg_humidity"),
        func.min(SensorData.humidity).label("min_humidity"),
        func.max(SensorData.humidity).label("max_humidity"),
        func.count(SensorData.id).label("total_records")
    )

    if device:
        query = query.filter(SensorData.device == device)

    result = await db.execute(query)
    return result.one()
