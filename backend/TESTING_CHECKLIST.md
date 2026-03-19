# OTP System Testing Checklist

## Pre-Testing Setup

- [ ] Backend running: `python -m uvicorn app.main:app --reload --port 8000`
- [ ] Frontend running: `npm run dev` (port 5174)
- [ ] Database seeded: `python populate_data.py`
- [ ] `.env` configured with SMS_PROVIDER (default: demo)

---

## Test 1: Demo Registration Flow

**Objective:** Test OTP registration with demo SMS provider

### Step 1: Start New Registration
1. Open: http://localhost:5174/register
2. Click "Register" tab
3. Select role: **Patient**
4. Fill form:
   - Email: `test.patient@example.com`
   - Phone: `+919876543210` (or any 10-digit number)
   - Password: `SecurePass123`
   - Confirm: `SecurePass123`
5. Click "Create Account"

**Expected:** 
- ✅ No errors
- ✅ Form sends to backend
- ✅ Backend logs: "SMS SENT TO +919876543210... OTP CODE: XXXXXX"

### Step 2: Get OTP from Console
1. Look at backend terminal/console
2. Find line containing: `"SMS SENT TO... OTP CODE:"`
3. Copy the 6-digit OTP code

**Example:**
```
SMS SENT TO +919876543210 | OTP CODE: 483729
```

### Step 3: Verify OTP
1. Frontend shows: "Enter the 6-digit code we sent"
2. Enter the OTP from Step 2
3. Click "Verify OTP"

**Expected:**
- ✅ No errors
- ✅ Backend logs: "OTP verified successfully"
- ✅ Redirects to Patient Dashboard
- ✅ JWT token stored in localStorage

### Step 4: Verify Auto-Login
1. Check browser console (F12)
2. Run: `localStorage.getItem('token')`
3. Should return JWT token (starts with `eyJ`)
4. Run: `localStorage.getItem('role')`
5. Should return: `patient`

**Expected:**
- ✅ Token in localStorage
- ✅ Role in localStorage
- ✅ Dashboard accessible without re-login

---

## Test 2: Login with Registered Account

**Objective:** Test login with bcrypt password verification

### Step 1: Logout
1. Click profile icon (top right)
2. Click "Logout"
3. Redirects to login page

### Step 2: Login with New Account
1. URL: http://localhost:5174/login
2. Email: `test.patient@example.com`
3. Password: `SecurePass123`
4. Click "Login"

**Expected:**
- ✅ Login successful
- ✅ Redirects to Patient Dashboard
- ✅ JWT token stored

### Step 3: Verify Password Hashing
1. Backend: Check database
   ```bash
   sqlite3 pulsesync.db "SELECT email, password FROM user LIMIT 1;"
   ```
2. Password should be **NOT** plaintext (looks like: `$2b$12$...`)

**Expected:**
- ✅ Password is bcrypt hash (starts with `$2b$`)
- ✅ Not plaintext password

---

## Test 3: Registration Validation

**Objective:** Test form validation and error handling

### Test 3.1: Invalid Password (Too Short)
1. Go to: http://localhost:5174/register
2. Fill form with:
   - Email: `test2@example.com`
   - Phone: `+919876543211`
   - Password: `Pass1` (only 5 characters, needs 6+)
3. Click "Create Account"

**Expected:**
- ✅ Error message: "Password must be at least 6 characters"
- ❌ No backend request sent

### Test 3.2: Password Mismatch
1. Fill with:
   - Password: `SecurePass123`
   - Confirm: `DifferentPass123`
3. Click "Create Account"

**Expected:**
- ✅ Error message: "Passwords do not match"
- ❌ No backend request sent

### Test 3.3: Duplicate Email
1. Try to register with: `test.patient@example.com` (already registered)
2. Click "Create Account"

**Expected:**
- ✅ Error from backend: "Email already registered"
- ✅ Returns to register page

### Test 3.4: Invalid Phone Number
1. Phone: `123` (too short)
2. Click "Create Account"

**Expected:**
- ✅ Error: "Invalid phone number"
- ❌ No backend request

---

## Test 4: OTP Expiry

**Objective:** Verify OTP expires after 5 minutes

### Step 1: Start Registration
1. Email: `test.expiry@example.com`
2. Phone: `+919876543212`
3. Password: `SecurePass123`
4. Click "Create Account"
5. Copy OTP from backend console

### Step 2: Wait 5+ Minutes
1. Don't enter OTP yet
2. Wait 5 minutes (or for testing: modify code to 1 minute)
3. Try entering OTP after expiry

**Expected:**
- ✅ Error: "OTP has expired"
- ✅ Must re-register to get new OTP

---

## Test 5: Invalid OTP

**Objective:** Verify wrong OTP is rejected

### Step 1: Start Registration
1. Email: `test.invalid@example.com`
2. Phone: `+919876543213`
3. Password: `SecurePass123`
4. Click "Create Account"
5. Copy OTP from backend console (e.g., `483729`)

### Step 2: Enter Wrong OTP
1. OTP field: `999999` (wrong)
2. Click "Verify OTP"

**Expected:**
- ✅ Error: "Invalid OTP"
- ✅ Can try again
- ✅ Same registration session continues

### Step 3: Enter Correct OTP
1. OTP field: `483729` (correct)
2. Click "Verify OTP"

**Expected:**
- ✅ Success
- ✅ Redirects to dashboard

---

## Test 6: Login Validation

**Objective:** Test login form validation

### Test 6.1: Wrong Password
1. Email: `test.patient@example.com` (existing account)
2. Password: `WrongPassword`
3. Click "Login"

**Expected:**
- ✅ Error: "Invalid email or password"

### Test 6.2: Non-existent Email
1. Email: `nonexistent@example.com`
2. Password: `Pass123`
3. Click "Login"

**Expected:**
- ✅ Error: "Invalid email or password"

### Test 6.3: Not Verified User
1. Pre-seeded accounts are verified
2. Manually create unverified user for this test
3. Try to login

**Expected:**
- ✅ Error: "Please verify your email first"

---

## Test 7: Register Multiple Roles

**Objective:** Test registration for different user roles

### Test 7.1: Register Doctor
1. Go to: http://localhost:5174/register
2. Select: **Doctor**
3. Fill form:
   - Email: `test.doctor@hospital.com`
   - Phone: `+919876543214`
   - Department: `Cardiology`
   - Password: `SecurePass123`
4. Get OTP from console, verify

**Expected:**
- ✅ Doctor profile created
- ✅ Department saved
- ✅ Redirects to Doctor Dashboard

### Test 7.2: Register Admin
1. Select: **Admin**
2. Fill and register (if admin registration is enabled)

**Expected:**
- ✅ Admin profile created
- ✅ Redirects to Admin Dashboard

---

## Test 8: Pre-seeded Accounts

**Objective:** Test login with pre-seeded test accounts

### Available Test Accounts
```
PATIENTS:
- email: john@example.com, password: patient123
- email: jane@example.com, password: patient123

DOCTORS:
- email: doctor1@hospital.com, password: doctor123
- email: doctor2@hospital.com, password: doctor123
```

### Test Each Account
1. Logout if logged in
2. Login with each email/password
3. Verify role and dashboard redirects correctly

**Expected:**
- ✅ All accounts login successfully
- ✅ Patient redirects to Patient Dashboard
- ✅ Doctor redirects to Doctor Dashboard

---

## Test 9: Backend Security Headers

**Objective:** Verify secure response headers

### Test 1: No OTP in Response
1. Use Chrome DevTools Network tab
2. Register, watch `/send-otp` request
3. Check Response JSON:
   ```json
   {
     "message": "OTP sent to your phone number",
     "otp_sent": true
   }
   ```

**Expected:**
- ✅ Response does NOT contain `otp_code` field
- ✅ Response does NOT contain actual OTP

### Test 2: No OTP in Network
1. Check Response headers and body
2. Verify no OTP anywhere in response

**Expected:**
- ✅ Only message and status in response
- ✅ OTP only exists in:
  - Backend console (demo mode)
  - Database (hashed time)
  - SMS message (sent to user)

---

## Test 10: Token Persistence

**Objective:** Verify JWT token is properly stored and used

### Step 1: Login
1. Login successfully
2. Verify dashboard loads

### Step 2: Refresh Page
1. Press F5 to refresh page
2. Dashboard should still load (token in localStorage)

**Expected:**
- ✅ Dashboard loads without re-login
- ✅ Token retrieved from localStorage
- ✅ User session persists

### Step 3: Open New Tab
1. Open new browser tab
2. Navigate to dashboard URL
3. Should redirect to login (no token in new session yet)

**Expected:**
- ✅ New tab requires login
- ✅ Each browser session has own localStorage

---

## Backend Verification Tests

### Check Password Hashing
```bash
cd backend
sqlite3 pulsesync.db

# See all users
SELECT email, password FROM user;

# Password should be bcrypt hash (starts with $2b$)
```

### Check OTP Fields
```sql
-- After registration (before OTP verification)
SELECT email, otp_code, otp_verified, otp_expiry FROM user WHERE email='test@example.com';

-- Should show:
-- email | otp_code | otp_verified | otp_expiry
-- Should have 6-digit code, FALSE, timestamp 5 min in future
```

### Check OTP After Verification
```sql
-- After verifying OTP
SELECT email, otp_code, otp_verified FROM user WHERE email='test@example.com';

-- Should show:
-- email | otp_code | otp_verified
-- NULL | 1 | (otp_code should be NULL/cleared)
```

---

## Performance Tests

### Test 1: Multiple Registrations
1. Register 5 different users rapidly
2. Each should work independently

**Expected:**
- ✅ All complete successfully
- ✅ No database locks
- ✅ No race conditions

### Test 2: Concurrent Logins
1. Open multiple tabs
2. Login in different tabs simultaneously

**Expected:**
- ✅ All generate different tokens
- ✅ All sessions work independently

---

## Final Checklist

- [ ] Demo registration works (OTP in console)
- [ ] OTP verification successful
- [ ] Auto-login after OTP verification
- [ ] Login with registered account works
- [ ] Password validation working (min 6 chars)
- [ ] OTP expiry after 5 minutes
- [ ] Invalid OTP rejected
- [ ] Wrong password rejected
- [ ] Password is bcrypt hashed
- [ ] Pre-seeded accounts login successfully
- [ ] Multiple roles register correctly
- [ ] Token persists after refresh
- [ ] No OTP in API responses
- [ ] JWT token in localStorage

---

## Troubleshooting Test Failures

### OTP Not Appearing in Console
1. Check SMS_PROVIDER in .env: `SMS_PROVIDER=demo`
2. Restart backend server
3. Check backend terminal is showing logs (not minimized)

### Backend Errors
1. Check all packages installed: `pip list | grep -E "bcrypt|twilio|python-dotenv"`
2. Verify .env exists in backend folder
3. Restart backend: `Ctrl+C` then restart

### Frontend Not Loading
1. Check port 5174 in browser
2. Run: `npm run dev` in frontend folder
3. Check for build errors in terminal

### Database Issues
1. Reset database: `rm pulsesync.db` then restart backend
2. Re-seed: `python populate_data.py`

---

## Quick Testing Session (15 minutes)

If you want to quickly test everything:

```bash
# Terminal 1: Start Backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Start Frontend
cd frontend
npm run dev

# Browser: Test Registration
1. Go to http://localhost:5174/register
2. Register new patient
3. Copy OTP from backend console
4. Verify OTP in frontend
5. Check dashboard loads

# Browser: Test Login
1. Logout
2. Login with test account: john@example.com / patient123
3. Verify login successful
```

**Total time:** ~5-10 minutes for full test cycle

---

**Next:** Once all tests pass, proceed to STEP 11 - Integration Testing
