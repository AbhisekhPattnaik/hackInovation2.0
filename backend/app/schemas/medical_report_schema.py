from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MedicalReportCreate(BaseModel):
    file_name: str
    file_type: str
    patient_id: int
    diagnosis: Optional[str] = None

class MedicalReportResponse(BaseModel):
    id: int
    patient_id: int
    file_name: str
    file_type: str
    diagnosis: Optional[str]
    created_at: datetime
    uploader_name: str
    status: Optional[str] = "pending"
    review_notes: Optional[str] = None
    findings: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    report_type: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True

class MedicalReportBase(BaseModel):
    file_name: str
    file_type: str
    diagnosis: Optional[str] = None

    class Config:
        from_attributes = True
