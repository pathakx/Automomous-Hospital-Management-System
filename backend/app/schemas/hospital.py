from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time, datetime

# --- DOCTOR SCHEMAS ---
class DoctorScheduleResponse(BaseModel):
    id: str
    day_of_week: str
    start_time: time
    end_time: time
    is_available: bool

    class Config:
        from_attributes = True

class DoctorResponse(BaseModel):
    id: str
    name: str
    specialization: str
    department: Optional[str] = None
    experience_years: int
    consultation_fee: float
    schedules: List[DoctorScheduleResponse] = []

    class Config:
        from_attributes = True

# --- APPOINTMENT SCHEMAS ---
class AppointmentCreate(BaseModel):
    doctor_id: str
    appointment_date: date
    appointment_time: time

class AppointmentResponse(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    appointment_date: date
    appointment_time: time
    status: str
    created_at: datetime
    doctor: Optional[DoctorResponse] = None

    class Config:
        from_attributes = True

# --- RECORD SCHEMAS ---
class PrescriptionResponse(BaseModel):
    id: str
    doctor_id: str
    medication: str
    dosage: str
    instructions: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class LabReportResponse(BaseModel):
    id: str
    report_type: str
    report_name: str
    file_url: str
    upload_date: datetime

    class Config:
        from_attributes = True

class BillResponse(BaseModel):
    id: str
    service_type: str
    amount: float
    payment_status: str
    created_at: datetime

    class Config:
        from_attributes = True

class BillPayment(BaseModel):
    bill_id: str
    payment_method: str

class PrescriptionCreate(BaseModel):
    patient_id: str
    appointment_id: Optional[str] = None
    medication: str
    dosage: str
    instructions: str