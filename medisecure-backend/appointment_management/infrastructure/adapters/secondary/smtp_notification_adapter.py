from typing import Optional
from uuid import UUID
from datetime import datetime
import os

from appointment_management.domain.ports.secondary.notification_port import NotificationPort
from patient_management.domain.ports.secondary.patient_repository_protocol import PatientRepositoryProtocol
from shared.ports.secondary.user_repository_protocol import UserRepositoryProtocol
from shared.ports.secondary.mailer_protocol import MailerProtocol

class SmtpNotificationAdapter(NotificationPort):
    """
    Adaptateur pour l'envoi de notifications via SMTP.
    Utilise le MailerProtocol pour l'envoi effectif des emails.
    """

    def __init__(
        self,
        mailer: MailerProtocol,
        patient_repository: PatientRepositoryProtocol,
        user_repository: UserRepositoryProtocol
    ):
        self.mailer = mailer
        self.patient_repository = patient_repository
        self.user_repository = user_repository
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

    async def send_appointment_created(
        self, 
        patient_id: UUID, 
        doctor_id: UUID, 
        appointment_id: UUID, 
        start_time: datetime
    ) -> None:
        """Notifie de la création d'un rendez-vous"""
        # Récupération des informations
        patient = await self.patient_repository.get_by_id(patient_id)
        doctor = await self.user_repository.get_by_id(doctor_id)

        if not patient or not patient.email:
            # Log warning: patient not found or no email
            return
        
        # Formatage de la date
        date_str = start_time.strftime("%d/%m/%Y à %H:%M")
        
        subject = "Confimation de votre rendez-vous - MediSecure"
        
        doctor_name = f"Dr. {doctor.last_name}" if doctor else "votre médecin"
        
        body = f"""
        Bonjour {patient.first_name} {patient.last_name},
        
        Votre rendez-vous avec {doctor_name} a été confirmé pour le {date_str}.
        
        Vous pouvez gérer vos rendez-vous sur votre espace patient : {self.frontend_url}
        
        Cordialement,
        L'équipe MediSecure
        """
        
        await self.mailer.send_email(
            to_email=patient.email,
            subject=subject,
            body=body
        )
        # On pourrait aussi notifier le médecin ici

    async def send_appointment_cancelled(
        self,
        patient_id: UUID,
        doctor_id: UUID,
        appointment_id: UUID,
        cancel_reason: str
    ) -> None:
        """Notifie de l'annulation d'un rendez-vous"""
        patient = await self.patient_repository.get_by_id(patient_id)
        doctor = await self.user_repository.get_by_id(doctor_id)

        if not patient or not patient.email:
            return

        doctor_name = f"Dr. {doctor.last_name}" if doctor else "votre médecin"

        subject = "Annulation de votre rendez-vous - MediSecure"
        
        body = f"""
        Bonjour {patient.first_name} {patient.last_name},
        
        Votre rendez-vous avec {doctor_name} a été annulé.
        
        Raison : {cancel_reason}
        
        Pour reprendre rendez-vous, veuillez vous connecter à votre espace : {self.frontend_url}
        
        Cordialement,
        L'équipe MediSecure
        """

        await self.mailer.send_email(
            to_email=patient.email,
            subject=subject,
            body=body
        )
