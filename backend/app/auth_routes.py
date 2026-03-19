from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database.sesion import get_db
from .models.user import User
from .models.patient import Patient
from .models.doctor import Doctor
from .schemas.user_schema import UserCreate, UserLogin, TokenResponse, RegisterRequest
from .auth import create_access_token
from .services.password_service import hash_password, verify_password, validate_password_strength

router = APIRouter()

@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user
    
    Security:
    - Password is validated and hashed using bcrypt
    - Account is immediately active after registration
    """
    
    # Validate password strength
    is_valid, message = validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    # Check if email already registered
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered. Please login instead.")
    
    # Hash password
    hashed_password = hash_password(request.password)
    
    # Create new user (immediately active, no OTP needed)
    user = User(
        name=request.name,
        email=request.email,
        phone_number=request.phone_number,
        password=hashed_password,
        role=request.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create patient or doctor profile
    if user.role == "patient":
        patient = Patient(user_id=user.id, severity_score=0.0)
        db.add(patient)
        db.commit()
    
    elif user.role == "doctor":
        doctor = Doctor(user_id=user.id, name=user.name)
        db.add(doctor)
        db.commit()
    
    # Generate JWT token
    access_token = create_access_token({
        "sub": user.email,
        "role": user.role
    })
    
    return {
        "message": "Registration successful! User verified.",
        "email": user.email,
        "verified": True,
        "access_token": access_token,
        "role": user.role
    }


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    User login with email and password
    
    Security:
    - Passwords are verified using bcrypt
    - JWT token is returned on success
    """
    
    db_user = db.query(User).filter(User.email == user.email).first()

    # Check if user exists
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password using bcrypt
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Create JWT token (no OTP verification required for login)
    token = create_access_token({
        "sub": db_user.email,
        "role": db_user.role
    })

    return {
        "access_token": token,
        "role": db_user.role,
        "email": db_user.email
    }
