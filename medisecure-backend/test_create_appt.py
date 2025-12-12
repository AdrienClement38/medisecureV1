import os
import json
import urllib.request
from jose import jwt
from datetime import datetime, timedelta
import uuid

# Values from docker-compose.yaml
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"

def create_token():
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode = {
        "sub": "00000000-0000-0000-0000-000000000000", # Admin ID
        "role": "ADMIN",
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def test_create_appointment(token):
    url = "http://localhost:8000/api/appointments/"
    
    # Data matching frontend logic
    data = {
        "patient_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", # Sophie Bernard
        "doctor_id": "00000000-0000-0000-0000-000000000000",
        "start_time": "2025-07-20T10:00:00",
        "end_time": "2025-07-20T10:30:00",
        "reason": "Test Appointment",
        "notes": "Testing creation"
    }
    
    json_data = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=json_data, method='POST')
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Content-Type', 'application/json')
    
    print(f"Calling {url} with data: {data}")
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Status: {response.status}")
            print(response.read().decode('utf-8'))
    except urllib.request.HTTPError as e:
        print(f"Status: {e.code}")
        print(e.read().decode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    token = create_token()
    test_create_appointment(token)
