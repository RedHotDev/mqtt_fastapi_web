from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from database import get_db
from schemas.schemas import SensorDataResponse, SensorDataCreate, SensorDataFilter
from services import sensor_service

router = APIRouter(prefix="/api/v1", tags=["sensors"])


@router.post("/sensors/data", response_model=SensorDataResponse)
async def create_sensor_data_endpoint(
    data: SensorDataCreate,
    db: Session = Depends(get_db)
):
    """Create new sensor data entry"""
    return sensor_service.create_sensor_data(db, data)
