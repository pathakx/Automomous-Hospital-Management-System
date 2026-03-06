from sqlalchemy import Column, String, Boolean, ForeignKey, Time
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    doctor_id = Column(String(36), ForeignKey("doctors.id"), nullable=False)
    day_of_week = Column(String, nullable=False) # e.g., 'Monday'
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)

    doctor = relationship("Doctor", back_populates="schedules")