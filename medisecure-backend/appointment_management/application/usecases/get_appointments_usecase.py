from datetime import datetime
from typing import List, Optional
from uuid import UUID
from appointment_management.domain.ports.secondary.appointment_repository_port import AppointmentRepositoryPort
from appointment_management.application.dtos.appointment_dto import AppointmentResponseDTO

class GetAppointmentsUseCase:
    """Use case to retrieve appointments with filters."""
    
    def __init__(self, appointment_repository: AppointmentRepositoryPort):
        self.appointment_repository = appointment_repository

    def execute(
        self, 
        patient_id: Optional[UUID] = None, 
        doctor_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AppointmentResponseDTO]:
        
        # Note: In a real implementation, we would pass these filters down to the repository
        # For now, we reuse the existing specific finder methods or fall back to basic logic
        # The prompt didn't specify a 'find_with_filters' method in the interface, 
        # so I will stick to what's available or adapt.
        
        appointments = []
        if patient_id:
            appointments = self.appointment_repository.find_all_by_patient_id(patient_id)
        elif doctor_id:
            appointments = self.appointment_repository.find_all_by_doctor_id(doctor_id)
        else:
            # If no ID filter, we might return empty or need a 'find_all'
            # For safety/performance, preventing full dump without filter
            return []
            
        # In-memory filtering for date range if repository doesn't support it directly in the interface I defined
        if start_date:
            appointments = [a for a in appointments if a.start_time >= start_date]
        if end_date:
            appointments = [a for a in appointments if a.end_time <= end_date]
            
        return [
            AppointmentResponseDTO(
                id=str(a.id),
                patient_id=str(a.patient_id),
                doctor_id=str(a.doctor_id),
                start_time=a.start_time.isoformat(),
                end_time=a.end_time.isoformat(),
                status=a.status,
                notes=a.notes,
                created_at=a.created_at.isoformat()
            )
            for a in appointments
        ]
