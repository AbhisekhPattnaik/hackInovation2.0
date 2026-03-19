"""
Comprehensive Doctor and Patient Appointment Management
Enhanced endpoints for fully functional appointment system
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from ..database.sesion import get_db
from ..models.appointment import Appointment
from ..models.doctor import Doctor
from ..models.patient import Patient
from ..models.user import User
from ..models.queue import QueueEntry
from ..services.explainability_service import ExplainabilityService
from ..services.reinforcement_learning_optimizer import ReinforcementLearningOptimizer
from ..services.timeseries_prediction import TimeSeriesPredictionService
from jose import jwt, JWTError
from ..auth import SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter(prefix="/appointments/advanced", tags=["Appointments - Advanced"])

class DoctorNotesRequest(BaseModel):
    notes: str
    diagnosis: str = None

class RescheduleRequest(BaseModel):
    new_slot_time: datetime
    reason: str

class AppointmentCompleteRequest(BaseModel):
    doctor_notes: str
    diagnosis: str = None

def get_doctor_from_token(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Extract doctor from bearer token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header")
    
    try:
        token_parts = authorization.split()
        if len(token_parts) != 2 or token_parts[0].lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        token = token_parts[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        role = payload.get("role")
        
        if not email or role != "doctor":
            raise HTTPException(status_code=403, detail="Not a doctor account")
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    doctor = db.query(Doctor).filter(Doctor.user_id == user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    
    return doctor

# IMPORTANT: Specific routes must come BEFORE generic {id} routes
@router.get("/doctor/today-queue")
def get_doctor_today_queue(
    doctor: Doctor = Depends(get_doctor_from_token),
    db: Session = Depends(get_db)
):
    """Get today's appointment queue for doctor"""
    
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    queue_entries = db.query(QueueEntry).filter(
        QueueEntry.doctor_id == doctor.id,
        QueueEntry.scheduled_time >= today_start,
        QueueEntry.scheduled_time <= today_end,
        QueueEntry.status.in_(["scheduled", "waiting", "in-progress"])
    ).order_by(QueueEntry.scheduled_time).all()
    
    appointments_list = []
    total_time = 0
    
    for idx, entry in enumerate(queue_entries):
        appointment = db.query(Appointment).filter(Appointment.id == entry.appointment_id).first()
        patient = db.query(Patient).filter(Patient.id == entry.patient_id).first()
        
        appointments_list.append({
            "position": idx + 1,
            "appointment_id": appointment.id if appointment else None,
            "queue_entry_id": entry.id,
            "patient_name": patient.user.name if patient and patient.user else "Unknown",
            "ps_id": patient.ps_id if patient else None,
            "scheduled_time": entry.scheduled_time,
            "predicted_duration": entry.predicted_consultation_duration,
            "severity": patient.severity_score if patient else 0,
            "priority": entry.priority_score,
            "no_show_risk": f"{entry.predicted_no_show_probability:.0%}",
            "status": entry.status
        })
        total_time += entry.predicted_consultation_duration
    
    return {
        "doctor_id": doctor.id,
        "doctor_name": doctor.user.name if doctor.user else "Unknown",
        "date": today.isoformat(),
        "queue_size": len(queue_entries),
        "total_estimated_time": total_time,
        "appointments": appointments_list
    }

@router.get("/{appointment_id}/details")
def get_appointment_details(
    appointment_id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get detailed appointment information"""
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    doctor = db.query(Doctor).filter(Doctor.id == appointment.doctor_id).first()
    patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
    
    # Calculate actual duration if completed
    actual_duration = None
    if appointment.start_time and appointment.end_time:
        actual_duration = int((appointment.end_time - appointment.start_time).total_seconds() / 60)
    
    return {
        "id": appointment.id,
        "doctor_id": appointment.doctor_id,
        "doctor_name": doctor.user.name if doctor and doctor.user else "Unknown",
        "doctor_specialization": doctor.specialization if doctor else None,
        "patient_id": appointment.patient_id,
        "patient_name": patient.user.name if patient and patient.user else "Unknown",
        "patient_ps_id": patient.ps_id if patient else None,
        "patient_severity": patient.severity_score if patient else None,
        "scheduled_time": appointment.slot_time,
        "actual_start_time": appointment.start_time,
        "actual_end_time": appointment.end_time,
        "actual_duration_minutes": actual_duration,
        "status": appointment.status,
        "symptoms": appointment.symptoms,
        "diagnosis": appointment.diagnosis,
        "doctor_notes": appointment.doctor_notes,
        "patient_review": appointment.patient_review,
        "created_at": appointment.created_at,
        "updated_at": appointment.updated_at
    }

@router.put("/{appointment_id}/reschedule")
def reschedule_appointment(
    appointment_id: int,
    request: RescheduleRequest,
    doctor: Doctor = Depends(get_doctor_from_token),
    db: Session = Depends(get_db)
):
    """Doctor reschedules an appointment with AI recommendation"""
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Verify doctor can reschedule this appointment
    if appointment.doctor_id != doctor.id:
        raise HTTPException(status_code=403, detail="Cannot reschedule another doctor's appointment")
    
    # Store original slot
    if not appointment.original_slot:
        appointment.original_slot = appointment.slot_time
    
    # Update appointment
    appointment.slot_time = request.new_slot_time
    appointment.reschedule_reason = request.reason
    appointment.status = "scheduled"
    appointment.updated_at = datetime.utcnow()
    
    # Update queue entry if exists
    queue_entry = db.query(QueueEntry).filter(QueueEntry.appointment_id == appointment_id).first()
    if queue_entry:
        queue_entry.scheduled_time = request.new_slot_time
        queue_entry.status = "scheduled"
    
    db.commit()
    db.refresh(appointment)
    
    return {
        "id": appointment.id,
        "new_slot_time": appointment.slot_time,
        "original_slot": appointment.original_slot,
        "reason": request.reason,
        "status": "rescheduled_successfully",
        "message": f"Appointment rescheduled to {request.new_slot_time}"
    }

@router.put("/{appointment_id}/complete")
def complete_appointment_with_notes(
    appointment_id: int,
    request: AppointmentCompleteRequest,
    doctor: Doctor = Depends(get_doctor_from_token),
    db: Session = Depends(get_db)
):
    """Complete appointment and add doctor notes"""
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Verify doctor can complete this appointment
    if appointment.doctor_id != doctor.id:
        raise HTTPException(status_code=403, detail="Cannot complete another doctor's appointment")
    
    # Set times if not already set
    if not appointment.start_time:
        appointment.start_time = datetime.utcnow()
    if not appointment.end_time:
        appointment.end_time = datetime.utcnow()
    
    # Update appointment
    appointment.status = "completed"
    appointment.doctor_notes = request.doctor_notes
    appointment.diagnosis = request.diagnosis
    appointment.updated_at = datetime.utcnow()
    
    # Update queue entry
    queue_entry = db.query(QueueEntry).filter(QueueEntry.appointment_id == appointment_id).first()
    if queue_entry:
        queue_entry.status = "completed"
    
    db.commit()
    db.refresh(appointment)
    
    return {
        "id": appointment.id,
        "status": "completed",
        "completed_at": appointment.end_time,
        "notes_saved": True,
        "message": "Appointment completed successfully"
    }

@router.get("/{appointment_id}/patient-details")
def get_patient_review(
    appointment_id: int,
    doctor: Doctor = Depends(get_doctor_from_token),
    db: Session = Depends(get_db)
):
    """Get patient information and medical history for appointment"""
    
    try:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Get patient's previous appointments with this doctor
        previous_appointments = db.query(Appointment).filter(
            Appointment.patient_id == appointment.patient_id,
            Appointment.doctor_id == doctor.id,
            Appointment.id != appointment_id,
            Appointment.status == "completed"
        ).order_by(Appointment.created_at.desc()).all()
        
        # Get patient's appointment history with other doctors
        all_appointments = db.query(Appointment).filter(
            Appointment.patient_id == appointment.patient_id,
            Appointment.id != appointment_id,
            Appointment.status == "completed"
        ).count()
        
        return {
            "patient_id": patient.id,
            "patient_name": patient.user.name if patient.user else "Unknown",
            "patient_email": patient.user.email if patient.user else None,
            "patient_phone": patient.user.phone_number if patient.user else None,
            "ps_id": patient.ps_id,
            "age": patient.age,
            "medical_conditions": getattr(patient, 'medical_conditions', None) or "Not provided",
            "medications": getattr(patient, 'medications', None) or "None",
            "allergies": getattr(patient, 'allergies', None) or "None",
            "severity_score": patient.severity_score,
            "no_show_count": patient.no_show_count,
            "late_arrival_count": patient.late_arrival_count,
            "previous_appointments_with_doctor": len(previous_appointments),
            "total_appointments_system": all_appointments,
            "previous_visits": [
                {
                    "id": appt.id,
                    "date": appt.slot_time,
                    "status": appt.status,
                    "notes": appt.doctor_notes,
                    "diagnosis": appt.diagnosis
                } for appt in previous_appointments[:5]
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching patient details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching patient details: {str(e)}")

@router.post("/{appointment_id}/schedule-recommendation")
def get_schedule_optimization(
    appointment_id: int,
    doctor: Doctor = Depends(get_doctor_from_token),
    db: Session = Depends(get_db)
):
    """Get RL-based schedule optimization recommendation"""
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    queue_entry = db.query(QueueEntry).filter(QueueEntry.appointment_id == appointment_id).first()
    if not queue_entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    
    # Get optimization recommendation
    recommendation = ReinforcementLearningOptimizer.recommend_slot_reassignment(queue_entry.id, db)
    
    # Generate explanation
    explanation = ExplainabilityService.generate_explanation(recommendation)
    
    return {
        "appointment_id": appointment_id,
        "recommendation": recommendation,
        "explanation": explanation,
        "confidence": recommendation.get("confidence", 0),
        "suggested_action": recommendation.get("recommendation", "no_change")
    }