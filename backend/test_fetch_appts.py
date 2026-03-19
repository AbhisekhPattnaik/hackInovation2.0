import requests

# Login
login_data = {'email': 'john@patient.com', 'password': 'patient123'}
login_response = requests.post('http://127.0.0.1:8000/login', json=login_data)
token = login_response.json()['access_token']

# Get appointments
headers = {'Authorization': f'Bearer {token}'}
appt_response = requests.get('http://127.0.0.1:8000/appointments/', headers=headers)

print('='*60)
print('TEST 3: FETCH APPOINTMENTS')
print('='*60)
print(f'Status: {appt_response.status_code}')

appointments = appt_response.json()
print(f'\nTotal appointments: {len(appointments)}')
print('\nAppointments:')
for appt in appointments:
    print(f'  • ID: {appt["id"]}, Doctor: {appt["doctor_name"]}, Time: {appt["slot_time"]}, Status: {appt["status"]}')
