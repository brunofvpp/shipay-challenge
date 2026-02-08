import secrets
import string
from typing import Final

from pwdlib import PasswordHash


def hash_password(password: str) -> str:
    pwd_hasher = PasswordHash.recommended()
    MAX_PASSWORD_LENGTH: Final[int] = 512
    if not password:
        raise ValueError("Password cannot be empty.")
    if len(password) > MAX_PASSWORD_LENGTH:
        password = password[:MAX_PASSWORD_LENGTH]
    return pwd_hasher.hash(password)


def generate_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))
