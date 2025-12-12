from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import controllers
from appointment_management.infrastructure.adapters.primary.controllers.appointment_controller import router as appointment_router
from patient_management.infrastructure.adapters.primary.controllers.patient_controller import router as patient_router
from api.controllers.auth_controller import router as auth_router

app = FastAPI(title="MediSecure API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(patient_router, prefix="/api")  # Adding /api prefix for consistency if desired, or root
app.include_router(appointment_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to MediSecure API"}