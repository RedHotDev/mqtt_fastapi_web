from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    datastamp = Column(DateTime, nullable=False, index=True)
    device = Column(String(100), nullable=False, index=True)
    temp = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<SensorData(device={self.device}, temp={self.temp}, humidity={self.humidity})>"
