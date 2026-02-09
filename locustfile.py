
import logging
import random
import uuid
from datetime import datetime, timedelta
from locust import HttpUser, task, between, events
from typing import Dict, Any

# Disable strict SSL warning if using self-signed certs
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MedisecureUser(HttpUser):
    abstract = True
    token: str = None
    user_id: str = None
    
    def on_start(self):
        self.login()

    def login(self):
        # Simulation of login based on role
        if isinstance(self, AdminUser):
            username = "admin@medisecure.com"
        elif isinstance(self, DoctorUser):
            username = "doctor1@medisecure.com"
        else:
            username = "patient1@medisecure.com"

        try:
            response = self.client.post("/api/auth/login", data={
                "username": username,
                "password": "Admin123!"  # Dev backdoor password
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.user_id = data["user"]["id"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
            else:
                logging.error(f"Login failed for {username}: {response.text}")
        except Exception as e:
            logging.error(f"Login exception: {str(e)}")

    @property
    def auth_headers(self):
        return getattr(self, "headers", {})

class PatientUser(MedisecureUser):
    weight = 3  # Higher weight = more users of this type
    wait_time = between(1, 5)

    @task(3)
    def view_my_appointments(self):
        # Patient viewing their own appointments
        if self.token:
            self.client.get(f"/api/appointments/?patient_id={self.user_id}", headers=self.auth_headers)

    @task(1)
    def create_appointment_attempt(self):
        # Attempt to create an appointment
        # Requires a valid doctor ID. Since we can't easily list doctors as a patient,
        # we'll use a random UUID to simulate load, expecting some 400s or 500s 
        # (or success if referential integrity isn't strictly enforced/mocked)
        # OR better: use our own ID as doctor just to pass validation if role check is loose
        # Realistically, we'd need a "Get Doctors" endpoint.
        
        if self.token:
            # Add random minutes (0 or 30) to vary slots
            random_minutes = random.choice([0, 30])
            start_time = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(days=random.randint(1, 30), hours=random.randint(8, 18), minutes=random_minutes)
            
            payload = {
                "patient_id": self.user_id,
                "doctor_id": "11111111-1111-1111-1111-111111111111", # Use valid doctor ID from init.sql 
                "start_time": start_time.isoformat(),
                "end_time": (start_time + timedelta(minutes=30)).isoformat(),
                "notes": "Patient requested appointment"
            }
            
            # We expect this might fail validation, but it tests the endpoint load
            with self.client.post("/api/appointments/", json=payload, headers=self.auth_headers, catch_response=True) as response:
                if response.status_code == 201:
                    response.success()
                elif response.status_code == 400 and "n'est pas disponible" in response.text:
                    # Conflict is a valid business logic response, not a system failure
                    response.success()
                elif response.status_code in [400, 500]:
                     response.failure(f"API Error: {response.text}")

class DoctorUser(MedisecureUser):
    weight = 2
    wait_time = between(1, 5)

    @task(2)
    def view_schedule(self):
        if self.token:
            # View schedule for next 7 days
            start = datetime.now()
            end = start + timedelta(days=7)
            self.client.get(
                f"/api/appointments/?doctor_id={self.user_id}&start_date={start.isoformat()}&end_date={end.isoformat()}",
                headers=self.auth_headers
            )

    @task(1)
    def view_patient_list(self):
        if self.token:
            self.client.get("/api/patients/?limit=10", headers=self.auth_headers)

class AdminUser(MedisecureUser):
    weight = 1
    wait_time = between(2, 10)

    @task(2)
    def manage_patients(self):
        if self.token:
            # List patients
            self.client.get("/api/patients/", headers=self.auth_headers)
            
            # Search patients
            search_payload = {
                "name": "a", # Broad search
                "skip": 0,
                "limit": 5
            }
            self.client.post("/api/patients/search", json=search_payload, headers=self.auth_headers)

    @task(1)
    def create_valid_appointment_flow(self):
        if self.token:
            # 1. Get a patient ID (using list)
            patients_resp = self.client.get("/api/patients/?limit=1", headers=self.auth_headers)
            if patients_resp.status_code == 200:
                patients = patients_resp.json().get("patients", [])
                if patients:
                    patient_id = patients[0]["id"]
                    
                    # 2. Create appointment
                    # Using admin's own ID as 'doctor_id' if admin is also a doctor or just to test
                    # Ideally we need a real doctor ID.
                    
                    start_time = datetime.now() + timedelta(days=random.randint(1, 30))
                    
                    payload = {
                        "patient_id": patient_id,
                        "doctor_id": self.user_id, # Using self as doctor proxy
                        "start_time": start_time.isoformat(),
                        "end_time": (start_time + timedelta(minutes=30)).isoformat(),
                        "notes": "Admin created appointment"
                    }
                    
                    self.client.post("/api/appointments/", json=payload, headers=self.auth_headers)
