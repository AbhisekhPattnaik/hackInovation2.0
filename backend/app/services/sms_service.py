import random
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_otp() -> str:
    """Generate random 6-digit OTP"""
    return str(random.randint(100000, 999999))

def send_otp_sms(phone_number: str, otp_code: str) -> bool:
    """
    Send OTP via SMS to phone number
    
    Supports:
    1. Twilio (global)
    2. Fast2SMS (India)
    3. Demo mode (console output for testing)
    
    Required environment variables:
    - SMS_PROVIDER: "twilio", "fast2sms", or "demo"
    - For Twilio:
      * TWILIO_ACCOUNT_SID
      * TWILIO_AUTH_TOKEN
      * TWILIO_PHONE_NUMBER
    - For Fast2SMS:
      * FAST2SMS_API_KEY
    
    NOTE: In demo mode only, OTP is printed to console for testing.
          In production (Twilio/Fast2SMS), OTP is NEVER printed.
    """
    
    try:
        sms_provider = os.getenv("SMS_PROVIDER", "demo").lower()
        
        if sms_provider == "twilio":
            return _send_via_twilio(phone_number, otp_code)
        elif sms_provider == "fast2sms":
            return _send_via_fast2sms(phone_number, otp_code)
        else:
            # Demo mode - print OTP to console for testing/development
            print(f"\n{'='*60}")
            print(f"📱 SMS SENT TO {phone_number}")
            print(f"{'='*60}")
            print(f"🔐 OTP CODE: {otp_code}")
            print(f"⏱️  Valid for: 5 minutes")
            print(f"{'='*60}\n")
            return True
            
    except Exception as e:
        print(f"⚠️ SMS Service Error: {str(e)}")
        return False

def _send_via_twilio(phone_number: str, otp_code: str) -> bool:
    """Send OTP using Twilio"""
    try:
        from twilio.rest import Client
        
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
        
        if not all([account_sid, auth_token, twilio_phone]):
            print("❌ Twilio credentials not configured in environment variables")
            return False
        
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=f"Your PulseSync OTP is: {otp_code}\n\nValid for 5 minutes. Do not share this OTP with anyone.",
            from_=twilio_phone,
            to=phone_number
        )
        
        # Log success without exposing OTP
        print(f"✅ SMS sent successfully to {phone_number} (Message ID: {message.sid})")
        return True
        
    except Exception as e:
        print(f"❌ Twilio error: {str(e)}")
        return False

def _send_via_fast2sms(phone_number: str, otp_code: str) -> bool:
    """Send OTP using Fast2SMS (India)"""
    try:
        api_key = os.getenv("FAST2SMS_API_KEY")
        
        if not api_key:
            print("❌ Fast2SMS API key not configured in environment variables")
            return False
        
        # Format phone number for India (remove +91 if present)
        formatted_phone = phone_number.replace("+91", "").replace(" ", "")
        if not formatted_phone.startswith("91"):
            formatted_phone = "91" + formatted_phone
        
        url = "https://www.fast2sms.com/dev/bulkSMS"
        headers = {
            "authorization": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "route": "otp",
            "numbers": formatted_phone,
            "message": f"Your PulseSync OTP is: {otp_code}\n\nValid for 5 minutes. Do not share this OTP with anyone."
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("return"):
                print(f"✅ SMS sent successfully to {phone_number}")
                return True
            else:
                print(f"❌ Fast2SMS error: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Fast2SMS HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Fast2SMS error: {str(e)}")
        return False

def verify_otp(stored_otp: str, provided_otp: str, expiry_time: datetime) -> tuple[bool, str]:
    """
    Verify OTP is correct and not expired
    
    Returns: (is_valid: bool, message: str)
    """
    
    try:
        # Convert both to strings and strip whitespace for comparison
        stored_str = str(stored_otp).strip() if stored_otp else ""
        provided_str = str(provided_otp).strip() if provided_otp else ""
        
        # Check if OTP not provided
        if not provided_str or not stored_str:
            return False, "Invalid OTP"
        
        # Check OTP match
        if stored_str != provided_str:
            return False, "Invalid OTP"
        
        # Check expiry
        if datetime.utcnow() > expiry_time:
            return False, "OTP expired"
        
        return True, "OTP verified successfully"
        
    except Exception as e:
        print(f"❌ OTP verification error: {str(e)}")
        return False, "OTP verification failed"

def get_otp_expiry() -> datetime:
    """Get expiry time (5 minutes from now)"""
    return datetime.utcnow() + timedelta(minutes=5)
