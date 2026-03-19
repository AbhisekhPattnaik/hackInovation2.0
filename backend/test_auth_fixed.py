import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("="*70)
print("TEST 1: LOGIN - Get Valid Token")
print("="*70)
login_data = {'email': 'john@patient.com', 'password': 'patient123'}
login_response = requests.post(f'{BASE_URL}/login', json=login_data)
print(f"Status: {login_response.status_code}")
if login_response.status_code == 200:
    token = login_response.json()['access_token']
    print(f"✅ Token received: {token[:50]}...")
else:
    print(f"❌ Login failed: {login_response.json()}")
    token = None

print("\n" + "="*70)
print("TEST 2: GET /appointments/ WITH VALID TOKEN")
print("="*70)
if token:
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/appointments/', headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
else:
    print("❌ No token available for this test")

print("\n" + "="*70)
print("TEST 3: GET /appointments/ WITHOUT TOKEN (should return 401)")
print("="*70)
response = requests.get(f'{BASE_URL}/appointments/')
print(f"Status: {response.status_code}")
if response.status_code == 401:
    print(f"✅ Correctly returned 401: {response.json()}")
else:
    print(f"❌ Expected 401 but got {response.status_code}: {response.json()}")

print("\n" + "="*70)
print("TEST 4: GET /appointments/ WITH INVALID TOKEN (should return 401)")
print("="*70)
invalid_headers = {'Authorization': 'Bearer invalid.token.here'}
response = requests.get(f'{BASE_URL}/appointments/', headers=invalid_headers)
print(f"Status: {response.status_code}")
if response.status_code == 401:
    print(f"✅ Correctly returned 401: {response.json()}")
else:
    print(f"❌ Expected 401 but got {response.status_code}: {response.json()}")

print("\n" + "="*70)
print("TEST 5: GET /users/me WITH VALID TOKEN")
print("="*70)
if token:
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/users/me', headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
else:
    print("❌ No token available for this test")

print("\n" + "="*70)
print("TEST 6: GET /users/me WITHOUT TOKEN (should return 401)")
print("="*70)
response = requests.get(f'{BASE_URL}/users/me')
print(f"Status: {response.status_code}")
if response.status_code == 401:
    print(f"✅ Correctly returned 401: {response.json()}")
else:
    print(f"❌ Expected 401 but got {response.status_code}: {response.json()}")
