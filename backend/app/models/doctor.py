from sqlalchemy import Column, String, Integer, Float, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    department = Column(String, nullable=True)
    experience_years = Column(Integer, default=0)
    consultation_fee = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    schedules = relationship("DoctorSchedule", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")
    prescriptions = relationship("Prescription", back_populates="doctor")