import urllib.request
import urllib.parse
import json

BASE_URL = "http://localhost:8000/api/auth/login"

users = [
    {"username": "doctor1@medisecure.com", "password": "Admin123!"},
    {"username": "patient1@medisecure.com", "password": "Admin123!"}
]

for user in users:
    try:
        data = urllib.parse.urlencode(user).encode()
        req = urllib.request.Request(BASE_URL, data=data, method='POST')
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                body = response.read().decode()
                token = json.loads(body).get('access_token')
                print(f"Login SUCCESS for {user['username']}")
                print(f"Token: {token[:10]}...")
            else:
                print(f"Login FAILED for {user['username']}: {response.status}")
    except urllib.error.HTTPError as e:
        print(f"Login FAILED for {user['username']}: {e.code}")
        print(e.read().decode())
    except Exception as e:
        print(f"Error connecting to API: {e}")
