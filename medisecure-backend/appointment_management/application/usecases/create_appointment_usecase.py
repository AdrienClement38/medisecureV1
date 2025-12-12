from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from appointment_management.domain.entities.appointment import Appointment
from appointment_management.domain.ports.secondary.appointment_repository_port import AppointmentRepositoryPort
from appointment_management.domain.ports.secondary.notification_port import NotificationPort
from appointment_management.application.dtos.appointment_dto import AppointmentResponseDTO, CreateAppointmentDTO

class CreateAppointmentUseCase:
    """
    Cas d'utilisation pour la création d'un rendez-vous
    """
    def __init__(
        self,
        appointment_repository: AppointmentRepositoryPort,
        notification_service: NotificationPort
    ):
        self.appointment_repository = appointment_repository
        self.notification_service = notification_service

    def execute(self, command: CreateAppointmentDTO) -> AppointmentResponseDTO:
        """
        Exécute le cas d'utilisation
        Args:
            command: DTO contenant les données nécessaires à la création
        Returns:
            DTO contenant les informations du rendez-vous créé
        Raises:
            ValueError: Si le créneau est déjà pris
        """
        # Vérifier si le créneau est disponible
        conflicts = self.appointment_repository.find_conflicts(
            doctor_id=command.doctor_id,
            start_time=command.start_time,
            end_time=command.end_time
        )
        if conflicts:
            raise ValueError("Le créneau horaire demandé n'est pas disponible")

        # Créer le rendez-vous
        appointment_id = uuid4()
        appointment = Appointment(
            id=appointment_id,
            patient_id=command.patient_id,
            doctor_id=command.doctor_id,
            start_time=command.start_time,
            end_time=command.end_time,
            notes=command.notes,
            status="scheduled"
        )

        # Sauvegarder le rendez-vous
        self.appointment_repository.save(appointment)

        # Envoyer une notification
        self.notification_service.send_appointment_created(
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            appointment_id=appointment.id,
            start_time=appointment.start_time
        )

        # Retourner le DTO de réponse
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
