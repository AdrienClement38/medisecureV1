import os
import json
import urllib.request
from jose import jwt
from datetime import datetime, timedelta

# Values from docker-compose.yaml
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"

def create_token():
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode = {
        "sub": "00000000-0000-0000-0000-000000000000", # Admin ID (from init.sql)
        "role": "ADMIN",
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def call_api(token):
    # Use localhost:8000 because we run inside container
    url = "http://localhost:8000/patients/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa" 
    # Note: controller prefix is /patients, mapped under /api in main?
    # Wait, main.py usually mounts /api. Let's check main.py or just try /patients first
    # In main.py, router prefix is often added.
    # I'll try the full URL likely used by frontend: /api/patients/...
    
    url = "http://localhost:8000/api/patients/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    
    print(f"Calling {url}")
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
    call_api(token)
