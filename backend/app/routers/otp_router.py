"""
OTP Router - Handles SMS OTP sending and verification for user registration
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from datetime import datetime

from ..database.sesion import get_db
from ..models.user import User
from ..services.otp_service import OTPService, OTPError
import secrets

router = APIRouter(prefix="/otp", tags=["OTP"])

# Store OTPs temporarily (in production: use Redis or database)
# Format: {phone_number: {"otp": "123456", "expiry": datetime, "attempts": 0}}
otp_store = {}

class SendOTPRequest(BaseModel):
    """Request schema for sending OTP"""
    phone_number: str = Field(..., min_length=10, max_length=15, description="Phone number with country code +1234567890")
    email: str = Field(..., description="Email for account verification")

class SendOTPResponse(BaseModel):
    """Response schema for OTP send"""
    message: str
    phone_number: str
    validity_minutes: int

class VerifyOTPRequest(BaseModel):
    """Request schema for OTP verification"""
    phone_number: str = Field(..., min_length=10, max_length=15)
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP")

class VerifyOTPResponse(BaseModel):
    """Response schema for OTP verification"""
    message: str
    verified: bool
    phone_number: str

@router.post("/send", response_model=SendOTPResponse)
async def send_otp(request: SendOTPRequest, db: Session = Depends(get_db)):
    """
    Send OTP to phone number
    
    **Steps:**
    1. Check if phone number already registered
    2. Generate 6-digit OTP
    3. Send via SMS (Twilio)
    4. Store OTP with 5-minute expiry
    5. Return success message
    
    **Parameters:**
    - phone_number: Phone number with country code (e.g., +14155552671)
    - email: Email address for account
    
    **Returns:**
    - message: "OTP sent successfully"
    - phone_number: The phone number OTP was sent to
    - validity_minutes: 5
    """
    
    # Normalize phone number (remove spaces, special chars)
    phone_number = ''.join(c for c in request.phone_number if c.isdigit() or c == '+')
    
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number
    
    # Check if phone already registered
    existing_user = db.query(User).filter(User.phone == phone_number).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    try:
        # Generate OTP
        otp_code = OTPService.generate_otp()
        
        # Send OTP via SMS
        sent = OTPService.send_otp(phone_number, otp_code)
        if not sent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP. Please try again."
            )
        
        # Store OTP with expiry
        expiry = OTPService.get_otp_expiry()
        otp_store[phone_number] = {
            "otp": otp_code,
            "expiry": expiry,
            "attempts": 0,
            "email": request.email
        }
        
        return SendOTPResponse(
            message="OTP sent successfully to your phone number",
            phone_number=phone_number,
            validity_minutes=5
        )
        
    except OTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/verify", response_model=VerifyOTPResponse)
async def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """
    Verify OTP sent to phone number
    
    **Steps:**
    1. Check if OTP exists for phone number
    2. Validate OTP matches and hasn't expired
    3. Limit verification attempts to 3
    4. Return verification result
    
    **Parameters:**
    - phone_number: Phone number with country code
    - otp: 6-digit OTP code
    
    **Returns:**
    - message: "OTP verified successfully" or error message
    - verified: Boolean
    - phone_number: The verified phone number
    
    **Error Cases:**
    - Phone number not found in OTP store (send OTP first)
    - OTP has expired (5 minutes)
    - OTP is incorrect (max 3 attempts)
    - Too many failed attempts
    """
    
    # Normalize phone number
    phone_number = ''.join(c for c in request.phone_number if c.isdigit() or c == '+')
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number
    
    # Check if OTP exists
    if phone_number not in otp_store:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OTP not found. Please request a new OTP."
        )
    
    otp_data = otp_store[phone_number]
    
    # Check if too many attempts
    if otp_data["attempts"] >= 3:
        del otp_store[phone_number]
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Request a new OTP."
        )
    
    # Verify OTP
    if not OTPService.verify_otp(request.otp, otp_data["otp"], otp_data["expiry"]):
        otp_data["attempts"] += 1
        remaining = 3 - otp_data["attempts"]
        
        if otp_data["attempts"] >= 3:
            del otp_store[phone_number]
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="OTP verification failed. Too many attempts."
            )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid OTP. {remaining} attempts remaining."
        )
    
    # OTP verified successfully
    # Clean up OTP from store (one-time use)
    verified_email = otp_data.get("email", "")
    del otp_store[phone_number]
    
    return VerifyOTPResponse(
        message="OTP verified successfully. You can now complete registration.",
        verified=True,
        phone_number=phone_number
    )

@router.get("/status/{phone_number}")
async def check_otp_status(phone_number: str):
    """
    Check if OTP is pending for a phone number
    (Development/debugging endpoint - remove in production)
    
    **Returns:**
    - has_otp: Boolean indicating if OTP is pending
    - expiry: When OTP expires
    - attempts: Number of verification attempts made
    """
    
    phone_number = ''.join(c for c in phone_number if c.isdigit() or c == '+')
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number
    
    if phone_number in otp_store:
        otp_data = otp_store[phone_number]
        return {
            "has_otp": True,
            "expiry": otp_data["expiry"],
            "attempts": otp_data["attempts"],
            "expired": datetime.utcnow() > otp_data["expiry"]
        }
    
    return {"has_otp": False}
