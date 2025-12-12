import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
from datetime import datetime, timedelta

from appointment_management.application.usecases.cancel_appointment_usecase import CancelAppointmentUseCase
from appointment_management.domain.entities.appointment import Appointment
from appointment_management.domain.ports.secondary.appointment_repository_port import AppointmentRepositoryPort
from appointment_management.domain.ports.secondary.notification_port import NotificationPort

class TestCancelAppointmentUseCase:
    
    @pytest.fixture
    def appointment_repository(self):
        return Mock(spec=AppointmentRepositoryPort)

    @pytest.fixture
    def notification_port(self):
        return Mock(spec=NotificationPort)

    @pytest.fixture
    def use_case(self, appointment_repository, notification_port):
        return CancelAppointmentUseCase(appointment_repository, notification_port)

    def test_cancel_appointment_success(self, use_case, appointment_repository, notification_port):
        # Arrange
        appointment_id = uuid4()
        patient_id = uuid4()
        doctor_id = uuid4()
        
        appointment = Appointment(
            id=appointment_id,
            patient_id=patient_id,
            doctor_id=doctor_id,
            start_time=datetime.now() + timedelta(days=1),
            end_time=datetime.now() + timedelta(days=1, hours=1),
            status="scheduled"
        )
        
        appointment_repository.find_by_id.return_value = appointment
        
        # Act
        use_case.execute(appointment_id, cancel_reason="Imprévu")
        
        # Assert
        assert appointment.status == "cancelled"
        appointment_repository.save.assert_called_once_with(appointment)
        notification_port.send_appointment_cancelled.assert_called_once_with(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_id=appointment_id,
            cancel_reason="Imprévu"
        )

    def test_cancel_appointment_not_found(self, use_case, appointment_repository):
        # Arrange
        appointment_id = uuid4()
        appointment_repository.find_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Appointment not found"):
            use_case.execute(appointment_id)
