from datetime import date

import pytest
from pydantic import ValidationError

from src.application.schemas import UserCreateInput, UserOutput


def test_user_create_input_strips_fields():
    # Arrange
    payload_data = {"name": "  Bruno  ", "email": "  bruno@fagundes.com ", "role_id": 1, "password": "  Senha123!  "}
    # Act
    payload = UserCreateInput(**payload_data)
    # Assert
    assert payload.name == "Bruno"
    assert payload.email == "bruno@fagundes.com"
    assert payload.password == "Senha123!"


def test_user_create_input_blank_password_raises():
    # Arrange / Act / Assert
    with pytest.raises(ValidationError):
        UserCreateInput(name="Bruno", email="bruno@fagundes.com", role_id=1, password="        ")


def test_password_validator_direct_call():
    # Arrange / Act / Assert
    with pytest.raises(ValueError):
        UserCreateInput._validate_password("        ")


def test_user_create_input_extra_fields_forbidden():
    # Arrange / Act / Assert
    with pytest.raises(ValidationError):
        UserCreateInput(name="Bruno", email="bruno@fagundes.com", role_id=1, password=None, extra_field="x")


def test_user_create_input_requires_positive_role_id():
    # Arrange / Act / Assert
    with pytest.raises(ValidationError):
        UserCreateInput(name="Bruno", email="bruno@fagundes.com", role_id=0, password=None)


def test_user_create_input_requires_valid_email():
    # Arrange / Act / Assert
    with pytest.raises(ValidationError):
        UserCreateInput(name="Bruno", email="not-an-email", role_id=1, password=None)


def test_user_output_from_attributes():
    # Arrange
    class UserObj:
        def __init__(self):
            self.id = 1
            self.name = "Bruno"
            self.email = "bruno@fagundes.com"
            self.role_id = 1
            self.created_at = date(2026, 2, 6)
            self.updated_at = None

    user_obj = UserObj()
    # Act
    output = UserOutput.model_validate(user_obj)
    # Assert
    assert output.id == 1
    assert output.email == "bruno@fagundes.com"
