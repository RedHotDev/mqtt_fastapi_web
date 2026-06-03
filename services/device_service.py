from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime
from models.models import SensorData, Device
from schemas.schemas import SensorDataCreate, SensorDataFilter, DeviceCreate, DeviceUpdate


async def device_create(db: AsyncSession, device_data: DeviceCreate) -> Device:
    """Асинхронное создание устройства"""
    exist_device = await db.execute(
        select(Device).where(Device.name == device_data.name))

    if exist_device.scalar_one_or_none():
        raise ValueError("Устройство уже существует")

    db_device = Device(
        name=device_data.name,
        description=device_data.description,
        is_active=1 if device_data.is_active else 0
    )

    db.add(db_device)
    await db.commit()
    await db.refresh(db_device)
    return db_device


async def get_devices(db: AsyncSession, device_active: bool = False) -> List[Device]:
    query = select(Device)

    if device_active:
        query = query.where(Device.is_active == 1)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_device_by_id(db: AsyncSession, device_id: int) -> Optional[Device]:
    """Получение устройства по ID"""
    result = await db.execute(
        select(Device).where(Device.id == device_id)
    )
    return result.scalar_one_or_none()


async def get_device_by_name(db: AsyncSession, name: str) -> Optional[Device]:
    """Получение устройства по имени"""
    result = await db.execute(
        select(Device).where(Device.name == name)
    )
    return result.scalar_one_or_none()


async def delete_device(db: AsyncSession, device_id: int) -> bool:
    """Удаление устройства """
    device = await get_device_by_id(db, device_id)
    if not device:
        return False

    await db.delete(device)
    await db.commit()

    return True
