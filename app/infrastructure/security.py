"""Adaptador Argon2id para almacenar contraseñas de forma segura."""
from argon2 import PasswordHasher as Argon2Hasher
from argon2.low_level import Type
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError


class Argon2PasswordHasher:
    def __init__(self) -> None:
        # Parámetros explícitos para que las decisiones de costo sean auditables.
        self._hasher = Argon2Hasher(time_cost=3, memory_cost=65536, parallelism=4,
                                    hash_len=32, salt_len=16, type=Type.ID)

    def generar_hash(self, password: str) -> str:
        return self._hasher.hash(password)

    def verificar(self, password: str, password_hash: str) -> bool:
        try:
            return self._hasher.verify(password_hash, password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False
