from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional
from uuid import UUID

class CreateAppointmentDTO(BaseModel):
    """DTO pour la création d'un rendez-vous"""
    patient_id: UUID
    doctor_id: UUID
    start_time: datetime
    end_time: datetime
    notes: Optional[str] = None

    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('La fin doit être après le début')
        return v

class AppointmentResponseDTO(BaseModel):
    """DTO pour la réponse à la création/lecture d'un rendez-vous"""
    id: str
    patient_id: str
    doctor_id: str
    start_time: str
    end_time: str
    status: str
    notes: Optional[str] = None
    created_at: str
