from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import desc
from jose import jwt, JWTError
from ..database.sesion import get_db
from ..models.prescription import Prescription
from ..models.patient import Patient
from ..models.doctor import Doctor
from ..models.user import User
from ..schemas.prescription_schema import PrescriptionCreate, PrescriptionResponse
from ..auth import SECRET_KEY, ALGORITHM
from datetime import datetime

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])

def get_current_user_from_token(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Extract current user from JWT token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        token_parts = authorization.split()
        if len(token_parts) != 2 or token_parts[0].lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        token = token_parts[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/my-prescriptions", response_model=list[PrescriptionResponse])
async def get_my_prescriptions(
    current_user = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Get all prescriptions for the current patient user"""
    # Find patient by user_id
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient record not found"
        )
    
    # Get all prescriptions ordered by most recent first
    prescriptions = db.query(Prescription).filter(
        Prescription.patient_id == patient.id
    ).order_by(desc(Prescription.prescription_date)).all()
    
    # Enrich with doctor names
    result = []
    for prescription in prescriptions:
        prescription_dict = {
            "id": prescription.id,
            "medication": prescription.medication,
            "dosage": prescription.dosage,
            "duration": prescription.duration,
            "days_supply": prescription.days_supply,
            "description": prescription.description,
            "patient_id": prescription.patient_id,
            "doctor_id": prescription.doctor_id,
            "prescription_date": prescription.prescription_date,
            "created_at": prescription.created_at,
            "doctor_name": prescription.doctor.name if prescription.doctor else "Dr. Unknown"
        }
        result.append(prescription_dict)
    
    return result

@router.post("/add", response_model=dict)
async def add_prescription(
    prescription_data: PrescriptionCreate,
    current_user = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Add a new prescription for a patient (doctor endpoint)"""
    # Verify the doctor exists and owns this prescription
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can add prescriptions"
        )
    
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == prescription_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Create new prescription
    new_prescription = Prescription(
        patient_id=prescription_data.patient_id,
        doctor_id=doctor.id,
        medication=prescription_data.medication,
        dosage=prescription_data.dosage,
        duration=prescription_data.duration,
        days_supply=prescription_data.days_supply,
        description=prescription_data.description,
        prescription_date=datetime.utcnow()
    )
    
    db.add(new_prescription)
    db.commit()
    db.refresh(new_prescription)
    
    return {
        "status": "success",
        "message": f"Prescription added for patient {patient.id}",
        "prescription_id": new_prescription.id
    }

@router.get("/doctor/patient/{patient_id}")
async def get_patient_prescriptions_by_doctor(
    patient_id: int,
    current_user = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Get all prescriptions for a specific patient (doctor view)"""
    # Verify the requesting user is a doctor
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can view patient prescriptions"
        )
    
    # Get all prescriptions for the patient
    prescriptions = db.query(Prescription).filter(
        Prescription.patient_id == patient_id
    ).order_by(desc(Prescription.prescription_date)).all()
    
    return {
        "patient_id": patient_id,
        "prescriptions": prescriptions,
        "count": len(prescriptions)
    }
