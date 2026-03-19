from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from ..database.sesion import get_db
from ..models.appointment import Appointment
from ..models.doctor import Doctor
from ..models.patient import Patient
from ..models.user import User
from ..schemas.appointment_schema import AppointmentCreate, AppointmentResponse
from ..services.severity_service import calculate_severity
from ..services.scheduling_service import assign_slot
from ..services.doctor_selection_service import select_best_doctor
from ..models.queue import QueueEntry
from ..services.prediction_service import PredictionService
from jose import jwt, JWTError
from ..auth import SECRET_KEY, ALGORITHM
import traceback


router = APIRouter(prefix="/appointments", tags=["Appointments"])


def get_current_user_from_header(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Extract user from bearer token"""
    if not authorization:
        print(f"❌ No authorization header provided")
        raise HTTPException(status_code=401, detail="No authorization header")
    
    try:
        token_parts = authorization.split()
        if len(token_parts) != 2 or token_parts[0].lower() != 'bearer':
            print(f"❌ Invalid Bearer token format")
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        token = token_parts[1]
        print(f"🔍 Decoding JWT token...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        role = payload.get("role")
        
        if not email:
            print(f"❌ No email in token")
            raise HTTPException(status_code=401, detail="Invalid token - no email")
        
        print(f"✅ Token decoded, email: {email}, role: {role}")
    except JWTError as jwt_err:
        print(f"❌ JWT Decode error: {str(jwt_err)}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(jwt_err)}")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"❌ User not found in database: {email}")
        raise HTTPException(status_code=404, detail="User not found")
    
    print(f"✅ User found: id={user.id}, name={user.name}")
    return {"user": user, "role": role, "email": email}


@router.get("/", response_model=list[AppointmentResponse])
def get_appointments(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get appointments for current user (patient gets their appointments, doctor gets theirs)"""
    
    print(f"\n📖 GET /appointments/ called")
    
    if not authorization:
        print(f"❌ No authorization header provided - returning 401")
        raise HTTPException(status_code=401, detail="Not authenticated - missing authorization header")
    
    try:
        print(f"🔍 Extracting user from authorization header...")
        user_info = get_current_user_from_header(authorization, db)
        user = user_info["user"]
        role = user_info["role"]
        
        print(f"✅ User authenticated: {user.email}, Role: {role}")
        
        if role == "patient":
            patient = db.query(Patient).filter(Patient.user_id == user.id).first()
            if not patient:
                print(f"❌ Patient profile not found for user {user.id}")
                raise HTTPException(status_code=404, detail="Patient profile not found")
            print(f"📖 Fetching appointments for patient_id: {patient.id}")
            appointments = db.query(Appointment).filter(Appointment.patient_id == patient.id).all()
            print(f"✅ Found {len(appointments) if appointments else 0} appointments for patient")
        elif role == "doctor":
            doctor = db.query(Doctor).filter(Doctor.user_id == user.id).first()
            if not doctor:
                print(f"❌ Doctor profile not found for user {user.id}")
                raise HTTPException(status_code=404, detail="Doctor profile not found")
            print(f"📖 Fetching appointments for doctor_id: {doctor.id}")
            appointments = db.query(Appointment).filter(Appointment.doctor_id == doctor.id).all()
            print(f"✅ Found {len(appointments) if appointments else 0} appointments for doctor")
        else:
            print(f"❌ Unknown role: {role}")
            raise HTTPException(status_code=400, detail="Invalid user role")
    except HTTPException:
        # Re-raise HTTPExceptions (401, 403, 404, etc.)
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    result = []
    for appointment in appointments:
        doctor = db.query(Doctor).filter(Doctor.id == appointment.doctor_id).first()
        patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
        
        doctor_name = doctor.user.name if doctor and doctor.user else "Unknown Doctor"
        patient_name = patient.user.name if patient and patient.user else "Unknown Patient"
        
        result.append(AppointmentResponse(
            id=appointment.id,
            doctor_id=appointment.doctor_id,
            patient_id=appointment.patient_id,
            doctor_name=doctor_name,
            patient_name=patient_name,
            slot_time=appointment.slot_time,
            status=appointment.status
        ))
    
    print(f"📖 Returning {len(result)} appointments")
    return result

@router.post("/", response_model=AppointmentResponse)
def create_appointment(data: AppointmentCreate, authorization: str = Header(None), db: Session = Depends(get_db)):
    print(f"\n" + "="*60)
    print(f"📝 POST /appointments/ called")
    print(f"{"="*60}")
    print(f"📝 Authorization header value: {'[PRESENT]' if authorization else '[MISSING]'}")
    if authorization:
        print(f"📝 Authorization header length: {len(authorization)} chars")
        print(f"📝 Authorization header starts with: {authorization[:50]}..." if len(authorization) > 50 else authorization)
    print(f"📝 Symptoms: {data.symptoms}")
    print(f"="*60)

    # Get user from token instead of requiring patient_id in body
    if not authorization:
        print("❌ No authorization header provided")
        raise HTTPException(status_code=401, detail="Not authenticated - missing authorization header")
    
    try:
        print(f"🔍 Extracting user from authorization header...")
        user_info = get_current_user_from_header(authorization, db)
        user = user_info["user"]
        role = user_info["role"]
        
        print(f"✅ User authenticated: {user.email}, role: {role}")
        
        if role != "patient":
            print(f"❌ User is not a patient, role is: {role}")
            raise HTTPException(status_code=403, detail="Only patients can book appointments")
        
        # Get patient profile from authenticated user
        print(f"🔍 Looking for patient profile for user_id: {user.id}")
        patient = db.query(Patient).filter(Patient.user_id == user.id).first()
        if not patient:
            print(f"❌ Patient profile not found for user {user.id}")
            raise HTTPException(status_code=404, detail="Patient profile not found")
        
        patient_id = patient.id
        print(f"✅ Patient found: ID={patient_id}")
    except HTTPException as http_err:
        print(f"❌ HTTP Exception: {http_err.detail}")
        raise
    except Exception as e:
        print(f"❌ Auth error: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

    try:
        severity_score = calculate_severity(data.symptoms)
        print(f"📝 Calculated severity: {severity_score}")

        patient_obj = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient_obj:
            print(f"❌ Patient with ID {patient_id} not found")
            raise HTTPException(status_code=404, detail="Patient not found")
        
        patient_obj.severity_score = severity_score
        db.commit()
        print(f"✅ Patient severity updated")

        # Use provided doctor_id if available, otherwise select best doctor based on symptoms
        doctor = None
        if data.doctor_id:
            print(f"🔍 Using user-selected doctor_id: {data.doctor_id}")
            doctor = db.query(Doctor).filter(Doctor.id == data.doctor_id).first()
            if not doctor:
                print(f"❌ Selected doctor ID {data.doctor_id} not found")
                raise HTTPException(status_code=404, detail=f"Doctor with ID {data.doctor_id} not found")
            print(f"✅ Using selected doctor: {doctor.id}")
        else:
            print(f"🔍 No doctor selected, selecting best doctor based on symptoms")
            doctor = select_best_doctor(db, data.symptoms)
            if not doctor:
                print(f"❌ No doctors available")
                raise HTTPException(status_code=404, detail="No doctors available")
            print(f"✅ Selected best doctor: {doctor.id}")

        # Assign slot
        slot_time = assign_slot(db, doctor.id, severity_score)
        print(f"✅ Assigned slot time: {slot_time}")

        appointment = Appointment(
            doctor_id=doctor.id,
            patient_id=patient_id,
            slot_time=slot_time,
            status="scheduled"
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        print(f"✅ Appointment created and committed to DB with ID: {appointment.id}")

        # Create queue entry for optimization
        try:
            predicted_duration = PredictionService.predict_consultation_duration(
                patient_id,
                doctor.id,
                severity_score,
                db
            )
            
            no_show_prob = PredictionService.predict_no_show_probability(patient_id, db)
            priority = PredictionService.calculate_priority_score(patient_id, severity_score, db)
            
            queue_entry = QueueEntry(
                appointment_id=appointment.id,
                patient_id=patient_id,
                doctor_id=doctor.id,
                status="scheduled",
                scheduled_time=slot_time,
                predicted_consultation_duration=predicted_duration,
                predicted_no_show_probability=no_show_prob,
                priority_score=priority
            )
            db.add(queue_entry)
            db.commit()
            print(f"✅ Queue entry created for appointment {appointment.id}")
        except Exception as e:
            print(f"⚠️ Queue entry creation error (non-fatal): {e}")

        # Fetch related data for response
        doctor_obj = db.query(Doctor).filter(Doctor.id == doctor.id).first()
        patient_response = db.query(Patient).filter(Patient.id == patient_id).first()
        
        doctor_name = doctor_obj.user.name if doctor_obj and doctor_obj.user else "Unknown Doctor"
        patient_name = patient_response.user.name if patient_response and patient_response.user else "Unknown Patient"

        response = AppointmentResponse(
            id=appointment.id,
            doctor_id=appointment.doctor_id,
            patient_id=appointment.patient_id,
            doctor_name=doctor_name,
            patient_name=patient_name,
            slot_time=appointment.slot_time,
            status=appointment.status
        )
        print(f"✅ Returning appointment response: {response}")
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Booking error: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create appointment: {str(e)}")


@router.put("/{appointment_id}/complete", response_model=AppointmentResponse)
def complete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    """Mark appointment as completed"""
    print(f"📝 PUT /appointments/{appointment_id}/complete called")
    
    # Verify user is authenticated
    current_user = get_current_user_from_header(authorization, db)
    
    # Get appointment
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        print(f"❌ Appointment not found: {appointment_id}")
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Verify doctor owns this appointment
    if appointment.doctor_id != current_user.doctor_id:
        print(f"❌ Unauthorized: Doctor {current_user.doctor_id} cannot complete appointment {appointment_id}")
        raise HTTPException(status_code=403, detail="Unauthorized to complete this appointment")
    
    # Update appointment status
    appointment.status = "completed"
    db.commit()
    db.refresh(appointment)
    
    # Update queue entry if exists
    queue_entry = db.query(QueueEntry).filter(QueueEntry.appointment_id == appointment_id).first()
    if queue_entry:
        queue_entry.status = "completed"
        db.commit()
    
    print(f"✅ Appointment {appointment_id} marked as completed")
    
    # Get related data for response
    doctor_obj = db.query(Doctor).filter(Doctor.id == appointment.doctor_id).first()
    patient_response = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
    
    doctor_name = doctor_obj.user.name if doctor_obj and doctor_obj.user else "Unknown Doctor"
    patient_name = patient_response.user.name if patient_response and patient_response.user else "Unknown Patient"

    return AppointmentResponse(
        id=appointment.id,
        doctor_id=appointment.doctor_id,
        patient_id=appointment.patient_id,
        doctor_name=doctor_name,
        patient_name=patient_name,
        slot_time=appointment.slot_time,
        status=appointment.status
    )