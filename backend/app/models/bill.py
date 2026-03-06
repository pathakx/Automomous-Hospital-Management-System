from sqlalchemy import Column, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class Bill(Base):
    __tablename__ = "bills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)
    service_type = Column(String, nullable=False) # e.g., 'Consultation', 'Lab Test'
    amount = Column(Float, nullable=False)
    payment_status = Column(String, default="pending") # pending, paid
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="bills")