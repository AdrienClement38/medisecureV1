from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    MISSED = "missed"

class Appointment:
    """Entité rendez-vous (indépendante de toute technologie)"""
    def __init__(
        self,
        id: UUID,
        patient_id: UUID,
        doctor_id: UUID,
        start_time: datetime,
        end_time: datetime,
        status: str = "scheduled",
        notes: Optional[str] = None,
        cancel_reason: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        self.notes = notes
        self.created_at = created_at or datetime.now()
        
        # Validation métier dans l'entité
        self._validate()

    def _validate(self) -> None:
        """Valide les règles métier de l'entité"""
        if self.end_time <= self.start_time:
            raise ValueError("La fin du rendez-vous doit être après le début")
        
        if (self.end_time - self.start_time).total_seconds() < 900:  # 15 minutes minimum
            raise ValueError("Un rendez-vous doit durer au moins 15 minutes")
            
        valid_statuses = ["scheduled", "confirmed", "cancelled", "completed"]
        if self.status not in valid_statuses:
            raise ValueError(f"Statut invalide. Valeurs autorisées: {valid_statuses}")

    def cancel(self, reason: Optional[str] = None) -> None:
        """Annuler un rendez-vous"""
        if self.status == "cancelled":
            raise ValueError("Le rendez-vous est déjà annulé")
        if self.status == "completed":
            raise ValueError("Impossible d'annuler un rendez-vous terminé")
        self.status = "cancelled"
        self.cancel_reason = reason
        
    def reschedule(self, new_start_time: datetime, new_end_time: datetime) -> None:
        """Reprogrammer un rendez-vous"""
        if self.status == "cancelled":
            raise ValueError("Impossible de reprogrammer un rendez-vous annulé")
        if self.status == "completed":
            raise ValueError("Impossible de reprogrammer un rendez-vous terminé")
            
        old_start = self.start_time
        old_end = self.end_time
        self.start_time = new_start_time
        self.end_time = new_end_time
        
        try:
            self._validate()
        except ValueError as e:
            # Restaurer les valeurs précédentes en cas d'erreur
            self.start_time = old_start
            self.end_time = old_end
            raise e