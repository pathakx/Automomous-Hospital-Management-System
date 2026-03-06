from sqlalchemy import Column, String, Date, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class Patient(Base):
    __tablename__ = "patients"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    blood_group = Column(String, nullable=True)
    allergies = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    appointments = relationship("Appointment", back_populates="patient")
    prescriptions = relationship("Prescription", back_populates="patient")
    reports = relationship("LabReport", back_populates="patient")
    bills = relationship("Bill", back_populates="patient")
    conversations = relationship("Conversation", back_populates="patient")