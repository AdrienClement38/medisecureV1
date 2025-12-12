import os
import json
import urllib.request
import urllib.parse
from jose import jwt
from datetime import datetime, timedelta

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

def test_fetch_calendar(token):
    # Simulate fetch for December 2025
    # Frontend sends: start_date=2025-12-01T00:00:00.000Z & end_date=2025-12-31T23:59:59.999Z (approx)
    
    params = {
        "start_date": "2025-12-01T00:00:00",
        "end_date": "2025-12-31T23:59:59"
    }
    query_string = urllib.parse.urlencode(params)
    url = f"http://localhost:8000/api/appointments/?{query_string}"
    
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    
    print(f"Calling {url}")
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Status: {response.status}")
            data = json.loads(response.read().decode('utf-8'))
            print(f"Data count: {len(data)}")
            print(json.dumps(data, indent=2))
    except urllib.request.HTTPError as e:
        print(f"Status: {e.code}")
        print(e.read().decode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    token = create_token()
    test_fetch_calendar(token)
