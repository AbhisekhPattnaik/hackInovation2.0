from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from ..database.sesion import get_db
from ..models.user import User
from ..schemas.user_schema import UserCreate, UserResponse
from ..models.doctor import Doctor
from ..models.patient import Patient
from jose import jwt, JWTError
from ..auth import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(
        name=user.name,
        email=user.email,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    if user.role == "doctor":
        doctor_profile = Doctor(user_id=db_user.id)
        db.add(doctor_profile)

    elif user.role == "patient":
        patient_profile = Patient(user_id=db_user.id)
        db.add(patient_profile)

    db.commit()

    return db_user

@router.get("/me")
def get_current_user_info(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Get current logged-in user info with their patient/doctor ID"""
    
    if not authorization:
        print("❌ No authorization header provided")
        raise HTTPException(status_code=401, detail="Not authenticated - missing authorization header")
    
    try:
        token_parts = authorization.split()
        if len(token_parts) != 2 or token_parts[0].lower() != 'bearer':
            print(f"❌ Invalid Bearer token format: {authorization[:50]}")
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        token = token_parts[1]
        print(f"🔍 Decoding JWT token for /me endpoint...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        role = payload.get("role")
        
        if not email:
            print(f"❌ No email in token")
            raise HTTPException(status_code=401, detail="Invalid token - no email")
        
        print(f"✅ Token decoded, email: {email}, role: {role}")
    except JWTError as jwt_err:
        print(f"❌ JWT Decode error: {str(jwt_err)}")
        raise HTTPException(status_code=401, detail=f"Invalid token")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"❌ User not found: {email}")
        raise HTTPException(status_code=404, detail="User not found")
    
    print(f"👤 Getting user info for: {user.email}, role: {role}")
    
    # Get patient or doctor ID
    patient_id = None
    doctor_id = None
    ps_id = None
    
    if role == "patient":
        patient = db.query(Patient).filter(Patient.user_id == user.id).first()
        if patient:
            patient_id = patient.id
            ps_id = patient.ps_id
            print(f"✅ Patient found: ID={patient_id}, PS_ID={ps_id}")
        else:
            print(f"⚠️ No patient profile found for user {user.id}, creating one...")
            # Auto-create patient profile if missing
            patient = Patient(user_id=user.id, severity_score=0.0)
            db.add(patient)
            db.commit()
            patient_id = patient.id
            ps_id = patient.ps_id
            print(f"✅ Patient profile auto-created: ID={patient_id}, PS_ID={ps_id}")
    elif role == "doctor":
        doctor = db.query(Doctor).filter(Doctor.user_id == user.id).first()
        if doctor:
            doctor_id = doctor.id
            print(f"✅ Doctor found: ID={doctor_id}")
        else:
            print(f"⚠️ No doctor profile found for user {user.id}, creating one...")
            # Auto-create doctor profile if missing
            doctor = Doctor(user_id=user.id, name=user.name)
            db.add(doctor)
            db.commit()
            doctor_id = doctor.id
            print(f"✅ Doctor profile auto-created: ID={doctor_id}")
    
    response = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "ps_id": ps_id
    }
    print(f"✅ Returning user info: {response}")
    return response


@router.get("/doctors")
def get_all_doctors(db: Session = Depends(get_db)):
    """Get list of all doctors with their info"""
    print(f"📋 GET /users/doctors called")
    
    doctors = db.query(Doctor).all()
    print(f"✅ Found {len(doctors)} doctors")
    
    response = []
    for doctor in doctors:
        doctor_data = {
            "id": doctor.id,
            "user_id": doctor.user_id,
            "name": doctor.name or (doctor.user.name if doctor.user else "Unknown"),
            "specialization": doctor.specialization or "General Medicine",
            "rating": doctor.rating,
            "utilization": doctor.utilization,
            "avg_consult_time": doctor.avg_consult_time,
            "years_of_experience": doctor.years_of_experience,
            "verification_status": doctor.verification_status
        }
        response.append(doctor_data)
    
    print(f"✅ Returning {len(response)} doctors")
    return response