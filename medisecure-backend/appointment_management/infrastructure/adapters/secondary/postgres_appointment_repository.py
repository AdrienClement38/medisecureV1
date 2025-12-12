from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from appointment_management.domain.entities.appointment import Appointment
from appointment_management.domain.ports.secondary.appointment_repository_port import AppointmentRepositoryPort
from appointment_management.infrastructure.models.appointment_model import AppointmentModel

class PostgreSQLAppointmentRepository(AppointmentRepositoryPort):
    """
    Adaptateur de repository pour persister les rendez-vous dans PostgreSQL
    """
    def __init__(self, session: Session):
        self.session = session

    def save(self, appointment: Appointment) -> None:
        """Sauvegarde un rendez-vous dans PostgreSQL"""
        # Vérifier si le rendez-vous existe déjà
        existing = self.session.query(AppointmentModel).filter(
            AppointmentModel.id == str(appointment.id)
        ).first()

        if existing:
            # Mise à jour
            existing.patient_id = str(appointment.patient_id)
            existing.doctor_id = str(appointment.doctor_id)
            existing.start_time = appointment.start_time
            existing.end_time = appointment.end_time
            existing.status = appointment.status
            existing.notes = appointment.notes
        else:
            # Création
            model = AppointmentModel(
                id=str(appointment.id),
                patient_id=str(appointment.patient_id),
                doctor_id=str(appointment.doctor_id),
                start_time=appointment.start_time,
                end_time=appointment.end_time,
                status=appointment.status,
                notes=appointment.notes,
                created_at=appointment.created_at
            )
            self.session.add(model)
        
        self.session.commit()

    def find_by_id(self, appointment_id: UUID) -> Optional[Appointment]:
        """Trouve un rendez-vous par son ID"""
        model = self.session.query(AppointmentModel).filter(
            AppointmentModel.id == str(appointment_id)
        ).first()
        if not model:
            return None
        return self._model_to_entity(model)

    def find_all_by_patient_id(self, patient_id: UUID) -> List[Appointment]:
        """Trouve tous les rendez-vous d'un patient"""
        models = self.session.query(AppointmentModel).filter(
            AppointmentModel.patient_id == str(patient_id)
        ).all()
        return [self._model_to_entity(model) for model in models]

    def find_all_by_doctor_id(self, doctor_id: UUID) -> List[Appointment]:
        """Trouve tous les rendez-vous d'un médecin"""
        models = self.session.query(AppointmentModel).filter(
            AppointmentModel.doctor_id == str(doctor_id)
        ).all()
        return [self._model_to_entity(model) for model in models]

    def find_conflicts(
        self, 
        doctor_id: UUID, 
        start_time: datetime, 
        end_time: datetime,
        exclude_appointment_id: Optional[UUID] = None
    ) -> List[Appointment]:
        """Trouve les rendez-vous en conflit pour un médecin"""
        query = self.session.query(AppointmentModel).filter(
            AppointmentModel.doctor_id == str(doctor_id),
            AppointmentModel.status.in_(["scheduled", "confirmed"]),
            or_(
                # Commence pendant un autre rendez-vous
                and_(
                    AppointmentModel.start_time <= start_time,
                    AppointmentModel.end_time > start_time
                ),
                # Termine pendant un autre rendez-vous
                and_(
                    AppointmentModel.start_time < end_time,
                    AppointmentModel.end_time >= end_time
                ),
                # Englobe complètement un autre rendez-vous
                and_(
                    AppointmentModel.start_time >= start_time,
                    AppointmentModel.end_time <= end_time
                )
            )
        )
        
        if exclude_appointment_id:
            query = query.filter(AppointmentModel.id != str(exclude_appointment_id))
            
        models = query.all()
        return [self._model_to_entity(model) for model in models]

    def _model_to_entity(self, model: AppointmentModel) -> Appointment:
        """Convertit un modèle SQLAlchemy en entité du domaine"""
        return Appointment(
            id=UUID(model.id),
            patient_id=UUID(model.patient_id),
            doctor_id=UUID(model.doctor_id),
            start_time=model.start_time,
            end_time=model.end_time,
            status=model.status,
            notes=model.notes,
            created_at=model.created_at
        )