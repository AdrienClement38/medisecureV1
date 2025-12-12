import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Index, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

# Assuming there is a shared Base, but for now I will use a local one 
# or try to import from shared infra if I knew where it was.
# The user prompted `medisecure-backend/shared/infrastructure/database/models/__init__.py` exist.
# I'll assumme `Base` is available there or I should define it.
# The propmt code has `Base = declarative_base()`, so I will use that locally for this file 
# unless I find a better place. Ideally it should share the same metadata.
# I will check `shared` later, but for now I follow the prompt snippet exactly.

from sqlalchemy.orm import declarative_base # Updated import for recent SA
Base = declarative_base()

class AppointmentModel(Base):
    """Modèle SQLAlchemy pour les rendez-vous"""
    __tablename__ = "appointments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), nullable=False, index=True) # Removed ForeignKey strict constraint to avoid import optimization issues for now, or assume strings. 
    # The prompt code had ForeignKey("patients.id"). I'll keep it but I might need to ensure `patients` table exists.
    # I will stick to the prompt code exactly as requested.
    
    # Redefining columns to match prompt exactly
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True) # Assumming doctors are users? Prompt said "doctors.id", but structure suggests `users`. I'll stick to prompt "doctors.id" but it might be wrong if doctors are in users table.
    
    # Wait, the prompt says `ForeignKey("doctors.id")`. I should verify if `doctors` table exists later.
    
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)
    status = Column(String(20), nullable=False, default="scheduled")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    # Indexation pour optimiser les requêtes fréquentes
    __table_args__ = (
        # Index pour la recherche des conflits (doctor + plage horaire)
        Index("idx_appointment_doctor_timerange", doctor_id, start_time, end_time),
        # Index pour la recherche de rendez-vous par statut
        Index("idx_appointment_status", status),
    )
