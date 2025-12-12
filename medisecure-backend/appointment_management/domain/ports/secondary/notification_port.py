from abc import ABC, abstractmethod
from uuid import UUID
from datetime import datetime

class NotificationPort(ABC):
    """Port pour l'envoi de notifications"""
    
    @abstractmethod
    def send_appointment_created(
        self, 
        patient_id: UUID, 
        doctor_id: UUID, 
        appointment_id: UUID, 
        start_time: datetime
    ) -> None:
        """Notifie de la création d'un rendez-vous"""
        pass

    @abstractmethod
    def send_appointment_cancelled(
        self,
        patient_id: UUID,
        doctor_id: UUID,
        appointment_id: UUID,
        cancel_reason: str
    ) -> None:
        """Notifie de l'annulation d'un rendez-vous"""
        pass
