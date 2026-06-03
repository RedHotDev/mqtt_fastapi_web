from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession  # Асинхронная сессия
from typing import List, Optional
from datetime import datetime
from database import get_db
from schemas.schemas import *
from services import sensor_service
from services import device_service

router = APIRouter(prefix="/api/v1", tags=["sensors"])


@router.post("/devices", response_model=DeviceResponse, status_code=201)
async def create_device_endpoint(
    device_data: DeviceCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать новое устройство"""
    try:
        return await device_service.device_create(db, device_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/device", response_model=List[DeviceResponse])
async def get_device_endpoint(device_active: bool = Query(False, description="Активные устройства") , db: AsyncSession = Depends(get_db)):
    """Получить список устройств"""
    return await device_service.get_devices(db, device_active)



@router.post("/sensors/data", response_model=SensorDataResponse)
async def create_sensor_data_endpoint(
    data: SensorDataCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new sensor data entry"""
    return await  sensor_service.create_sensor_data(db, data)


@router.get("/sensors/data", response_model=List[SensorDataResponse])
async def get_sensor_data_endpoint(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000,
                       description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Получить список данных датчиков"""
    return await sensor_service.get_sensor_data(db, skip, limit)


@router.get("/sensor/data/{device_id}", response_model=List[SensorDataResponse])
async def get_sensor_data_by_device_endpoint(
    device_id: int,
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Получить данные по устройству"""
    return await sensor_service.get_sensor_data_by_device_id(db, device_id, limit)



@router.get("/sensor/data", response_model=List[SensorDataResponse])
async def get_sensor_data_filter_endpoint( 
        device_id: Optional[int] = Query(None, description="ID устройства"),
        tag: Optional[str] = Query(None, description="Тег датчика"),
        limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
        db: AsyncSession = Depends(get_db)
):
    """Получить данные по фильтру"""
    
    filter_obj = SensorDataFilter(
        device=device_id,
        tag=tag
    )
    
    return await sensor_service.get_sensor_data_filter(db, filter_obj, limit)


@router.get("/sensors/device_sensor_data", response_model=List[DeviceSensorData])
async def get_sensor_data_endpoint(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000,
                       description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Получить список данных датчиков"""
    return await sensor_service.get_device_sensor_data(db,  limit)
