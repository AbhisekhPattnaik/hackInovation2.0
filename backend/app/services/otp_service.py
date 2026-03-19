"""
OTP Service for SMS verification using Twilio
Generates, sends, and verifies OTP codes
"""

import random
import string
from datetime import datetime, timedelta, timezone
import os

# In production, use: from twilio.rest import Client

class OTPService:
    """
    OTP Service - Handles SMS OTP generation and verification
    In production: Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER in env
    """
    
    # For testing purposes, we'll log to console (but never show OTP to user)
    # In production: Use Twilio SDK
    
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "your_account_sid")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "your_auth_token")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+1234567890")
    
    OTP_VALIDITY_MINUTES = 5
    OTP_LENGTH = 6
    
    @staticmethod
    def generate_otp() -> str:
        """Generate a 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=OTPService.OTP_LENGTH))
    
    @staticmethod
    def send_otp(phone_number: str, otp_code: str) -> bool:
        """
        Send OTP via SMS using Twilio
        Returns: True if sent successfully, False otherwise
        
        NOTE: OTP is NOT logged in console in production
        """
        try:
            # In production, uncomment and use Twilio:
            # from twilio.rest import Client
            # client = Client(OTPService.TWILIO_ACCOUNT_SID, OTPService.TWILIO_AUTH_TOKEN)
            # message = client.messages.create(
            #     body=f"Your PulseSync OTP is: {otp_code}. Valid for 5 minutes. Do not share.",
            #     from_=OTPService.TWILIO_PHONE_NUMBER,
            #     to=phone_number
            # )
            # return message.sid is not None
            
            # For development/testing (without actually sending SMS):
            # Log only for debugging, NEVER expose to user
            print(f"[DEV-ONLY] OTP Request for {phone_number}: {otp_code}")  # Local testing only
            return True
            
        except Exception as e:
            print(f"Error sending OTP: {str(e)}")
            return False
    
    @staticmethod
    def verify_otp(provided_otp: str, stored_otp: str, expiry_time: datetime) -> bool:
        """
        Verify OTP by comparing provided OTP with stored OTP and checking expiry
        """
        if not provided_otp or not stored_otp:
            return False
        
        # Check if OTP has expired
        if datetime.utcnow() > expiry_time:
            return False
        
        # Compare OTPs (timing-safe comparison in production)
        return provided_otp.strip() == stored_otp.strip()
    
    @staticmethod
    def get_otp_expiry() -> datetime:
        """Get OTP expiry time (current time + 5 minutes)"""
        return datetime.utcnow() + timedelta(minutes=OTPService.OTP_VALIDITY_MINUTES)

class OTPError(Exception):
    """Base OTP Exception"""
    pass

class OTPValidationError(OTPError):
    """Raised when OTP validation fails"""
    pass

class OTPExpiredError(OTPError):
    """Raised when OTP has expired"""
    pass

class OTPSendFailedError(OTPError):
    """Raised when OTP sending fails"""
    pass
