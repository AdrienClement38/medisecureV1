from uuid import UUID
from appointment_management.domain.ports.secondary.appointment_repository_port import AppointmentRepositoryPort
from appointment_management.domain.ports.secondary.notification_port import NotificationPort

class CancelAppointmentUseCase:
    """Use case to cancel an appointment."""

    def __init__(
        self, 
        appointment_repository: AppointmentRepositoryPort,
        notification_port: NotificationPort
    ):
        self.appointment_repository = appointment_repository
        self.notification_port = notification_port

    def execute(self, appointment_id: UUID, cancel_reason: str = "Motif non spécifié") -> None:
        appointment = self.appointment_repository.find_by_id(appointment_id)
        if not appointment:
            raise ValueError("Appointment not found")
        
        appointment.cancel()
        self.appointment_repository.save(appointment)

        # Envoyer la notification
        self.notification_port.send_appointment_cancelled(
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            appointment_id=appointment.id,
            cancel_reason=cancel_reason
        )
