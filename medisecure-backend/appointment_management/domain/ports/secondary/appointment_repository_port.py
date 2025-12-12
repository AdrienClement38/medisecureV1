from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from appointment_management.domain.entities.appointment import Appointment

class AppointmentRepositoryPort(ABC):
    """
    Port pour le repository de rendez-vous.
    Interface que les adaptateurs de persistance doivent implémenter.
    """
    @abstractmethod
    def save(self, appointment: Appointment) -> None:
        """Sauvegarde un rendez-vous"""
        pass

    @abstractmethod
    def find_by_id(self, appointment_id: UUID) -> Optional[Appointment]:
        """Trouve un rendez-vous par son ID"""
        pass

    @abstractmethod
    def find_all_by_patient_id(self, patient_id: UUID) -> List[Appointment]:
        """Trouve tous les rendez-vous d'un patient"""
        pass

    @abstractmethod
    def find_all_by_doctor_id(self, doctor_id: UUID) -> List[Appointment]:
        """Trouve tous les rendez-vous d'un médecin"""
        pass

    @abstractmethod
    def find_conflicts(
        self, 
        doctor_id: UUID, 
        start_time: datetime, 
        end_time: datetime,
        exclude_appointment_id: Optional[UUID] = None
    ) -> List[Appointment]:
        """
        Trouve les rendez-vous en conflit pour un médecin
        sur une plage horaire donnée
        """
        pass

    @abstractmethod
    def find_all(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Appointment]:
        """
        Trouve tous les rendez-vous, avec filtrage optionnel par date
        """
        pass
