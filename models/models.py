from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Integer, default=1)  # 1 - активен, 0 - неактивен
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Связь с сенсорными данными
    sensor_data = relationship("SensorData", back_populates="device_rel")

    def __repr__(self):
        return f"<Device(id={self.id}, name='{self.name}')>"


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey(
        "devices.id", ondelete="CASCADE"), nullable=False, index=True)
    datestamp = Column(DateTime, nullable=False, index=True)
    tag = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    device_rel = relationship("Device", back_populates="sensor_data")
    
    def __repr__(self):
        return f"<SensorData(device_id={self.device_id}, tag='{self.tag}', datestamp='{self.datestamp}', value={self.value})>"
