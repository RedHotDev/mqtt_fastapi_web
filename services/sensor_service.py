from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime
from models.models import SensorData
from schemas.schemas import SensorDataCreate, SensorDataFilter


def create_sensor_data(db: Session, data: SensorDataCreate) -> SensorData:
    """Create new sensor data entry with proper commit"""
    db_data = SensorData(**data.model_dump())
    db.add(db_data)
    db.commit()  # Explicit commit
    db.refresh(db_data)
    return db_data




