# SMS Provider Setup Guide

## Quick Comparison

| Provider | Cost | Coverage | Setup Time | Best For |
|----------|------|----------|-----------|----------|
| **Demo** | Free | None | 0 min | Development |
| **Twilio** | ~$0.0075/SMS | Worldwide | 5-10 min | Global apps |
| **Fast2SMS** | ~₹0.30/SMS | India focused | 2-3 min | Indian users |

## 1. Demo Mode (Default - Recommended for Development)

No setup required! OTP will be printed in backend console.

### Run with Demo Mode
```bash
# 1. In backend/.env, ensure:
SMS_PROVIDER=demo

# 2. Start backend
python -m uvicorn app.main:app --reload --port 8000

# 3. Register user
# OTP will print in console: "SMS SENT TO... OTP CODE: 123456"

# 4. Use the OTP from console in frontend
```

**Pros:**
- ✅ Free
- ✅ No setup needed
- ✅ Instant testing
- ✅ Perfect for development

**Cons:**
- ❌ No actual SMS sent
- ❌ OTP printed in console (security risk in production)
- ❌ Only for testing

---

## 2. Twilio Setup (Global Coverage)

### Cost
- $0.0075 per SMS (varies by country)
- $15 trial credit (usually covers 2000+ OTP messages)

### Step-by-Step Setup

#### 1. Create Twilio Account
1. Visit: https://www.twilio.com/console
2. Sign up with email
3. Verify phone number
4. Click "Get Started"

#### 2. Get Credentials
1. Go to Dashboard: https://www.twilio.com/console
2. Find these credentials:
   - **Account SID** (starts with "AC")
   - **Auth Token** (hidden, click eye icon to reveal)
3. Go to Phone Numbers section
4. Copy your Twilio Phone Number (e.g., +1234567890)

#### 3. Add to Backend
1. Create/edit `backend/.env`:
```bash
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=AC1234567890abcdef
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

2. Ensure bcrypt and twilio packages are installed:
```bash
pip install bcrypt twilio python-dotenv
```

3. Start backend:
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

#### 4. Test Registration
1. Register with real phone number
2. Check phone for SMS with OTP
3. Enter OTP in frontend
4. Auto-logged in ✅

### Twilio Account Types

**Trial Account (Free for 30 days):**
- $15 credit
- Must verify phone numbers to send SMS
- Works for development & testing

**Paid Account:**
- $0.0075 per outbound SMS
- Send SMS to any number
- Many other features available

### Upgrade from Trial to Paid
1. Go to Account Settings
2. Change account type
3. Add payment method
4. Now can send SMS to any number

---

## 3. Fast2SMS Setup (India-Focused)

### Cost
- Very affordable (₹0.30-0.50 per SMS)
- Instant activation
- Best for Indian users

### Step-by-Step Setup

#### 1. Create Fast2SMS Account
1. Visit: https://www.fast2sms.com
2. Sign up with email / phone
3. Email verification
4. Login to dashboard

#### 2. Get API Key
1. Go to Dashboard
2. Look for "API KEY" or "Integration"
3. Copy your API Key (long alphanumeric string)

#### 3. Add to Backend
1. Create/edit `backend/.env`:
```bash
SMS_PROVIDER=fast2sms
FAST2SMS_API_KEY=your_api_key_here
```

2. Start backend:
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

#### 4. Test Registration
1. Register with Indian phone number (10 digits)
2. Check phone for SMS with OTP
3. Enter OTP in frontend
4. Auto-logged in ✅

### Phone Number Format
Fast2SMS requires proper formatting:
- Correct: `9876543210` or `+919876543210`
- Invalid: `+1-987-654-3210`

---

## Switching Providers

### From Demo to Twilio
```bash
# backend/.env
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
```

Restart backend - automatic ✅

### From Twilio to Fast2SMS
```bash
# backend/.env
SMS_PROVIDER=fast2sms
FAST2SMS_API_KEY=your_key
```

Restart backend - automatic ✅

### Back to Demo
```bash
# backend/.env
SMS_PROVIDER=demo
```

Restart backend - automatic ✅

---

## Troubleshooting

### Issue: "SMS Service Error"

**Check 1: Provider Set Correctly**
```bash
# Should be one of:
SMS_PROVIDER=demo
SMS_PROVIDER=twilio
SMS_PROVIDER=fast2sms
```

**Check 2: Credentials Valid**
```bash
# Twilio - verify credentials are correct
# Fast2SMS - check API key in dashboard
```

**Check 3: Backend Restarted**
```bash
# After changing .env, restart:
# Ctrl+C to stop
# python -m uvicorn app.main:app --reload --port 8000
```

### Issue: Twilio - SMS Not Sent
1. **Trial account?** - Verify recipient phone number in console
2. **Wrong phone format?** - Use: +1 (country code) (number)
3. **Out of credits?** - Check account balance
4. **Invalid token?** - Double-check credentials from console

### Issue: Fast2SMS - SMS Not Sent
1. **API key valid?** - Copy from dashboard again
2. **Account active?** - Check dashboard for any messages
3. **Indian number?** - Should be 10 digits or +91...
4. **Enough credits?** - Check account balance in dashboard

### Issue: "ModuleNotFoundError: twilio"
```bash
pip install twilio
```

### Issue: "OTP in console but still says demo"
1. Check `SMS_PROVIDER` in `.env` is set correctly
2. Restart backend server
3. Try again

---

## Production Checklist

- [ ] Use **Paid Twilio** or **Fast2SMS** account (not trial)
- [ ] Store credentials in environment variables safely
- [ ] **Never** commit `.env` to version control
- [ ] Add `.env` to `.gitignore`:
  ```
  .env
  .env.local
  *.db
  __pycache__/
  ```
- [ ] Set `DEBUG=False` in production
- [ ] Use `SECRET_KEY` with random 32+ character string
- [ ] Enable HTTPS
- [ ] Monitor SMS costs
- [ ] Set up alerts for failed SMS

---

## Cost Estimation

### Monthly SMS Costs (1000 OTP messages)

| Provider | Cost | Notes |
|----------|------|-------|
| **Demo** | $0 | Development only |
| **Twilio** | ~$7.50 | Global, reliable |
| **Fast2SMS** | ~₹300 ($3.60) | India-focused, cheap |

### For Scaling (10,000 OTPs/month):
- **Twilio:** ~$75/month
- **Fast2SMS:** ~₹3,000 ($36)/month
- **Demo:** Unlimited free (development)

---

## Next Steps

1. **Choose provider** (Demo for testing, Twilio/Fast2SMS for production)
2. **Get credentials** (if not using Demo)
3. **Update `.env`** with credentials
4. **Restart backend** server
5. **Test registration** with real phone number
6. **Check SMS delivery** in your phone
7. **Monitor costs** if using paid provider

---

**Questions?** Check the full documentation in `OTP_SYSTEM_DOCUMENTATION.md`
