from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status

from appointment_management.application.dtos.appointment_dto import AppointmentResponseDTO, CreateAppointmentDTO
from appointment_management.application.usecases.create_appointment_usecase import CreateAppointmentUseCase
from appointment_management.application.usecases.cancel_appointment_usecase import CancelAppointmentUseCase
from appointment_management.application.usecases.get_appointments_usecase import GetAppointmentsUseCase
from shared.container.container import Container
from shared.services.authenticator.extract_token import extract_token_payload

router = APIRouter(prefix="/appointments", tags=["appointments"])

def get_container():
    """Fournit le container d'injection de dépendances."""
    return Container()

@router.post("/", response_model=AppointmentResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    data: CreateAppointmentDTO,
    token_payload: Dict[str, Any] = Depends(extract_token_payload),
    container: Container = Depends(get_container)
):
    """Crée un nouveau rendez-vous"""
    try:
        # Instantiation du Use Case via le Container
        use_case = CreateAppointmentUseCase(
            appointment_repository=container.appointment_repository(),
            notification_service=container.notification_service()
        )
        result = use_case.execute(data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_appointment(
    appointment_id: UUID,
    cancel_reason: str = Query("Non spécifié", description="Raison de l'annulation"),
    token_payload: Dict[str, Any] = Depends(extract_token_payload),
    container: Container = Depends(get_container)
):
    """Annule un rendez-vous existant"""
    try:
        use_case = CancelAppointmentUseCase(
            appointment_repository=container.appointment_repository(),
            notification_port=container.notification_service()
        )
        use_case.execute(appointment_id, cancel_reason=cancel_reason)
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

@router.get("/", response_model=List[AppointmentResponseDTO])
async def get_appointments(
    patient_id: Optional[UUID] = Query(None),
    doctor_id: Optional[UUID] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    token_payload: Dict[str, Any] = Depends(extract_token_payload),
    container: Container = Depends(get_container)
):
    """Récupère une liste de rendez-vous avec possibilité de filtrage"""
    try:
        use_case = GetAppointmentsUseCase(
            appointment_repository=container.appointment_repository()
        )
        result = use_case.execute(
            patient_id=patient_id,
            doctor_id=doctor_id,
            start_date=start_date,
            end_date=end_date
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")