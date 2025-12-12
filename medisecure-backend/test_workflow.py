import os
import json
import urllib.request
import urllib.parse
from jose import jwt
from datetime import datetime, timedelta
import uuid

# Values from docker-compose.yaml
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"

def create_token():
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode = {
        "sub": "00000000-0000-0000-0000-000000000000",
        "role": "ADMIN",
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def run_workflow():
    token = create_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # 1. Create Appointment
    appt_date = "2025-12-15"
    start_time = f"{appt_date}T10:00:00"
    end_time = f"{appt_date}T10:30:00"
    
    payload = {
        "patient_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "doctor_id": "00000000-0000-0000-0000-000000000000",
        "start_time": start_time,
        "end_time": end_time,
        "notes": "Test workflow appointment"
    }

    print("1. Creating Appointment...")
    req = urllib.request.Request(
        "http://localhost:8000/api/appointments/",
        data=json.dumps(payload).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Creation Status: {response.status}")
            data = json.loads(response.read().decode('utf-8'))
            print("Created:", json.dumps(data, indent=2))
            created_id = data.get('id')
    except urllib.request.HTTPError as e:
        print(f"Creation Failed: {e.code}")
        print(e.read().decode('utf-8'))
        return

    # 2. Fetch Calendar
    print("\n2. Fetching Calendar...")
    params = {
        "start_date": f"{appt_date}T00:00:00",
        "end_date": f"{appt_date}T23:59:59"
    }
    query_string = urllib.parse.urlencode(params)
    url = f"http://localhost:8000/api/appointments/?{query_string}"
    
    req_fetch = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req_fetch) as response:
            print(f"Fetch Status: {response.status}")
            data = json.loads(response.read().decode('utf-8'))
            print(f"Found {len(data)} appointments")
            found = False
            for appt in data:
                if appt.get('id') == created_id:
                    print("SUCCESS: Created appointment found in fetch!")
                    found = True
                    break
            if not found:
                print("FAILURE: Created appointment NOT found in fetch response.")
    except Exception as e:
        print(f"Fetch Error: {e}")

if __name__ == "__main__":
    run_workflow()
