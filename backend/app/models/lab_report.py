from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class LabReport(Base):
    __tablename__ = "lab_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)
    report_type = Column(String, nullable=False) # blood, radiology, etc.
    report_name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="reports")