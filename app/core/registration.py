"""Reglas de registro: independientes del transporte HTTP."""
from datetime import datetime, timezone
from uuid import uuid4

from .models import Credencial, Usuario
from .repositories import PasswordHasher, UserRepository


class CorreoDuplicado(Exception):
    pass


class RegistroInvalido(Exception):
    pass


class RegistroService:
    def __init__(self, usuarios: UserRepository, hasher: PasswordHasher) -> None:
        self._usuarios = usuarios
        self._hasher = hasher

    def registrar(self, nombre: str, correo: str, password: str, confirmacion: str) -> Usuario:
        nombre = nombre.strip()
        correo = correo.strip().casefold()
        if not nombre or not correo or len(password) < 12 or password != confirmacion:
            raise RegistroInvalido("Datos de registro inválidos")
        if self._usuarios.buscar_por_correo(correo) is not None:
            raise CorreoDuplicado("El correo ya está registrado")
        usuario = Usuario(id=uuid4(), nombre=nombre, email_normalizado=correo,
                          creado_en=datetime.now(timezone.utc))
        credencial = Credencial(usuario_id=usuario.id,
                                password_hash=self._hasher.generar_hash(password))
        try:
            self._usuarios.crear_cuenta(usuario, credencial)
        except ValueError as exc:
            if str(exc) == "Cuenta duplicada":
                raise CorreoDuplicado("El correo ya está registrado") from exc
            raise
        return usuario
