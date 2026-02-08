import pytest

from src.application import security as utils


def test_hash_password_truncates_long_value():
    # Arrange
    password = "a" * 600
    # Act
    hashed = utils.hash_password(password)
    # Assert
    assert hashed.startswith("$argon2")


def test_hash_password_rejects_empty():
    # Arrange / Act / Assert
    with pytest.raises(ValueError):
        utils.hash_password("")


def test_hash_password_trims_super_long_values_and_returns_different_hash():
    # Arrange
    password = "abc123!" * 200
    # Act
    hashed = utils.hash_password(password)
    # Assert
    assert hashed.startswith("$argon2")
    assert password not in hashed


def test_generate_password_length_and_charset():
    # Arrange / Act
    password = utils.generate_password(length=20)
    # Assert
    assert len(password) == 20
    assert all(char in utils.string.ascii_letters + utils.string.digits + "!@#$%&*" for char in password)


def test_generate_password_uses_default_length():
    # Arrange / Act
    password = utils.generate_password()
    # Assert
    assert len(password) == 16
