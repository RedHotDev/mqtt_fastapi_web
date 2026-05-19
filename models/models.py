from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    device = Column(Integer, nullable=False, index=True)
    datestamp = Column(DateTime, nullable=False, index=True)
    tag = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<SensorData(device={self.device}, tag='{self.tag}', datestamp='{self.datestamp}', value={self.value})>"
