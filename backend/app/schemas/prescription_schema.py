from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PrescriptionBase(BaseModel):
    medication: str
    dosage: Optional[str] = None
    duration: Optional[str] = None
    days_supply: Optional[int] = None
    description: Optional[str] = None

class PrescriptionCreate(PrescriptionBase):
    patient_id: int
    doctor_id: int

class PrescriptionResponse(PrescriptionBase):
    id: int
    patient_id: int
    doctor_id: int
    doctor_name: Optional[str] = None
    prescription_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True
