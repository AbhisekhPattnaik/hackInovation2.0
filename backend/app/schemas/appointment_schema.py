from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class AppointmentCreate(BaseModel):
    symptoms: List[str]
    patient_id: Optional[int] = None  # Optional - will be extracted from JWT token
    doctor_id: Optional[int] = None  # Optional - if provided, uses this doctor instead of auto-selection
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    doctor_name: Optional[str] = None
    patient_name: Optional[str] = None
    slot_time: datetime
    status: str

    class Config:
        from_attributes = True