from datetime import datetime
from uuid import UUID
from appointment_management.domain.ports.secondary.appointment_repository_port import AppointmentRepositoryPort
from appointment_management.application.dtos.appointment_dto import AppointmentResponseDTO

class RescheduleAppointmentUseCase:
    """Use case to reschedule an appointment."""

    def __init__(self, appointment_repository: AppointmentRepositoryPort):
        self.appointment_repository = appointment_repository

    def execute(self, appointment_id: UUID, new_start_time: datetime, new_end_time: datetime) -> AppointmentResponseDTO:
        appointment = self.appointment_repository.find_by_id(appointment_id)
        if not appointment:
            raise ValueError("Appointment not found")
            
        # Check conflicts for the new time, excluding the current appointment
        conflicts = self.appointment_repository.find_conflicts(
            doctor_id=appointment.doctor_id,
            start_time=new_start_time,
            end_time=new_end_time,
            exclude_appointment_id=appointment_id
        )
        if conflicts:
            raise ValueError("Le créneau horaire demandé n'est pas disponible")
            
        appointment.reschedule(new_start_time, new_end_time)
        self.appointment_repository.save(appointment)
        
        return AppointmentResponseDTO(
            id=str(appointment.id),
            patient_id=str(appointment.patient_id),
            doctor_id=str(appointment.doctor_id),
            start_time=appointment.start_time.isoformat(),
            end_time=appointment.end_time.isoformat(),
            status=appointment.status,
            notes=appointment.notes,
            created_at=appointment.created_at.isoformat()
        )
