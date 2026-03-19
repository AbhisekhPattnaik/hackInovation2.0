# PulseSync OTP Registration System Documentation

## Overview
This document describes the complete OTP (One-Time Password) based registration and authentication system for PulseSync.

## Architecture

### Registration Flow

```
1. User fills registration form
   ↓
2. POST /send-otp
   - Generate 6-digit OTP
   - Hash password using bcrypt
   - Store user with OTP (expires in 5 minutes)
   - Send OTP via SMS (Twilio/Fast2SMS)
   - Return: `{ "otp_sent": true }`
   ↓
3. User receives OTP on phone
   ↓
4. User enters OTP on verification page
   ↓
5. POST /verify-otp
   - Check OTP matches
   - Verify OTP not expired
   - Mark user as verified
   - Clear OTP from database
   - Create patient/doctor profile
   - Generate JWT token
   - Return: `{ "access_token": "...", "role": "..." }`
   ↓
6. User authenticated & redirected to dashboard
```

## API Endpoints

### 1. Send OTP - `/send-otp` (POST)

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone_number": "+1234567890",
  "password": "SecurePassword123",
  "role": "patient"
}
```

**Response (Success - 200):**
```json
{
  "message": "OTP sent to your phone number",
  "email": "john@example.com",
  "phone_number": "+1234567890",
  "otp_sent": true
}
```

**Response (Error - 400):**
```json
{
  "detail": "Email already registered. Please login instead."
}
```

**Security Features:**
- ✅ Password validated for minimum length (6 characters)
- ✅ Password hashed using bcrypt before storage
- ✅ OTP NOT returned in response
- ✅ OTP NOT logged to console
- ✅ OTP stored with 5-minute expiry
- ✅ Overwrites previous OTP if user resends

### 2. Verify OTP - `/verify-otp` (POST)

**Request:**
```json
{
  "email": "john@example.com",
  "otp_code": "123456"
}
```

**Response (Success - 200):**
```json
{
  "message": "Registration successful! User verified.",
  "email": "john@example.com",
  "verified": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "role": "patient"
}
```

**Response (Error - 400):**
```json
{
  "detail": "Invalid OTP"
}
```

```json
{
  "detail": "OTP expired"
}
```

**Security Features:**
- ✅ OTP must match exactly
- ✅ OTP must be within 5-minute window
- ✅ OTP cleared after verification
- ✅ JWT token generated and returned
- ✅ User automatically created patient/doctor profile
- ✅ User can now login

### 3. Login - `/login` (POST)

**Request:**
```json
{
  "email": "john@example.com",
  "password": "SecurePassword123"
}
```

**Response (Success - 200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "role": "patient",
  "email": "john@example.com"
}
```

**Security Features:**
- ✅ Password verified using bcrypt
- ✅ Account must be OTP verified
- ✅ JWT token returned on success

## SMS Provider Configuration

### DEMO Mode (Default - No SMS Sent)
```bash
SMS_PROVIDER=demo
```
- No actual SMS sent
- Perfect for development/testing
- Users need to manually track their OTP

### Twilio Integration

**Setup Steps:**
1. Create Twilio account: https://www.twilio.com/console
2. Get:
   - Account SID
   - Auth Token
   - Twilio Phone Number (e.g., +1234567890)

3. Add to `.env`:
```bash
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

4. Install (if not already):
```bash
pip install twilio
```

**Cost:** ~$0.0075 per SMS in most countries

### Fast2SMS Integration (India-Focused)

**Setup Steps:**
1. Create Fast2SMS account: https://www.fast2sms.com
2. Get API Key from dashboard
3. Add to `.env`:
```bash
SMS_PROVIDER=fast2sms
FAST2SMS_API_KEY=your_api_key
```

**Cost:** Very affordable for Indian users

## Database Schema

### User Table Changes
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    phone_number VARCHAR,
    password VARCHAR NOT NULL,  -- Bcrypt hashed
    role VARCHAR,  -- 'patient' or 'doctor'
    otp_code VARCHAR,  -- Temporary, cleared on verify
    otp_verified BOOLEAN DEFAULT FALSE,  -- True after OTP verification
    otp_expiry DATETIME,  -- Expires in 5 minutes
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Password Security

### Bcrypt Hashing
- Algorithm: bcrypt
- Cost factor: 12 rounds
- Hash format: `$2b$12$...` (60 characters)

**Password Verification:**
```python
from app.services.password_service import verify_password

is_valid = verify_password(user_entered_password, stored_hash)
```

### Password Validation
- Minimum 6 characters
- (Optional: Can require uppercase, lowercase, and digits)

## Environment Variables

Create `.env` file in backend directory:
```bash
# Database
DATABASE_URL=sqlite:///./pulsesync.db

# JWT
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256

# SMS Provider (demo, twilio, fast2sms)
SMS_PROVIDER=demo

# Twilio (if using Twilio)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# Fast2SMS (if using Fast2SMS)
FAST2SMS_API_KEY=

# Application
APP_NAME=PulseSync
DEBUG=True
FRONTEND_URL=http://localhost:5173
```

## Frontend Integration

### Register Component
1. User fills register form (name, email, phone, password, role)
2. Submit → Calls `/send-otp`
3. Navigate to OTP verification page

### OTP Verification Component
1. User enters 6-digit OTP
2. Submit → Calls `/verify-otp`
3. On success:
   - Store token: `localStorage.setItem("token", response.access_token)`
   - Store role: `localStorage.setItem("role", response.role)`
   - Redirect to dashboard based on role

### Login Component
1. User enters email & password
2. Submit → Calls `/login`
3. On success:
   - Store token
   - Store role
   - Redirect to dashboard

## Testing

### Test Accounts (Demo Mode)
```
Patient:
Email: john@patient.com
Password: patient123
Phone: +1234567890

Doctor:
Email: ahmed@hospital.com
Password: doctor123
Phone: +9876543210
```

### Testing OTP Flow
1. Change `SMS_PROVIDER=demo` in `.env`
2. Register with phone number
3. OTP will be printed in backend console
4. Enter OTP in frontend verification form

### Testing with Real SMS
1. Get Twilio/Fast2SMS account
2. Update `.env` with credentials
3. Register with real phone number
4. Receive actual SMS with OTP

## Security Best Practices

### ✅ Implemented
- [x] Passwords hashed with bcrypt (12 rounds)
- [x] OTP not returned in API response
- [x] OTP not logged to console
- [x] OTP expires in 5 minutes
- [x] OTP cleared after verification
- [x] JWT token generation
- [x] Environment variables for secrets
- [x] HTTPS recommended in production

### ⚠️ Additional Recommendations
- [ ] Rate limiting on `/send-otp` endpoint
- [ ] Rate limiting on `/verify-otp` endpoint
- [ ] Max 3 OTP verification attempts per OTP
- [ ] Lock account after 5 failed login attempts
- [ ] Email verification as additional security
- [ ] HTTPS in production
- [ ] Rotate JWT secret regularly
- [ ] Log authentication attempts (without passwords)

## Troubleshooting

### Issue: "OTP sent but not received"
**Solution:** Check `SMS_PROVIDER` setting in `.env`
- If `demo`: OTP printed in backend console
- If `twilio`: Verify credentials and phone number format
- If `fast2sms`: Account may have credits issue

### Issue: "Invalid OTP"
**Solution:**
- Check OTP not expired (5 minutes)
- Check OTP entered correctly (6 digits)
- Check OTP matches what was sent (if in demo, check console)

### Issue: "Email already registered"
**Solution:** If email exists and verified, must use `/login` endpoint

### Issue: "Account pending OTP verification"
**Solution:** Complete OTP verification at `/send-otp` → `/verify-otp`

## Code References

**OTP Generation:**
- File: `services/sms_service.py`
- Function: `generate_otp()`
- Returns: 6-digit random OTP

**Password Hashing:**
- File: `services/password_service.py`
- Functions: `hash_password()`, `verify_password()`
- Algorithm: bcrypt

**Auth Routes:**
- File: `auth_routes.py`
- Endpoints: `/send-otp`, `/verify-otp`, `/login`

**SMS Sending:**
- File: `services/sms_service.py`
- Functions: `send_otp_sms()`, `_send_via_twilio()`, `_send_via_fast2sms()`

## Deployment Checklist

- [ ] Change `SECRET_KEY` to random value (min 32 chars)
- [ ] Set `DEBUG=False`
- [ ] Configure SMS provider (Twilio or Fast2SMS)
- [ ] Set proper `FRONTEND_URL` for CORS
- [ ] Use HTTPS in production
- [ ] Implement rate limiting
- [ ] Set up database backups
- [ ] Monitor failed login attempts
- [ ] Review and rotate secrets regularly

---

## Version History

**v1.0.0** (Current)
- ✅ OTP-based registration with SMS
- ✅ Bcrypt password hashing
- ✅ Twilio integration
- ✅ Fast2SMS integration
- ✅ JWT token generation
- ✅ Environment variable configuration
- ✅ Demo mode for testing
