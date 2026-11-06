"""Autenticación: no depende de FastAPI, cookies ni almacenamiento concreto."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import secrets
from uuid import UUID

from .models import Sesion
from .repositories import PasswordHasher, SessionRepository, UserRepository


class CredencialesInvalidas(Exception):
    pass


@dataclass(frozen=True, slots=True)
class InicioExitoso:
    token: str
    usuario_id: UUID
    expira_en: datetime


class LoginService:
    def __init__(self, usuarios: UserRepository, sesiones: SessionRepository,
                 hasher: PasswordHasher, hash_ficticio: str) -> None:
        self._usuarios = usuarios
        self._sesiones = sesiones
        self._hasher = hasher
        self._hash_ficticio = hash_ficticio

    def iniciar(self, correo: str, password: str) -> InicioExitoso:
        normalizado = correo.strip().casefold()
        usuario = self._usuarios.buscar_por_correo(normalizado)
        credencial = self._usuarios.buscar_credencial(usuario.id) if usuario else None
        hash_a_verificar = credencial.password_hash if credencial else self._hash_ficticio
        valido = self._hasher.verificar(password, hash_a_verificar)
        if not usuario or not credencial or not valido:
            raise CredencialesInvalidas()
        ahora = datetime.now(timezone.utc)
        # 256 bits de entropía, opaco y sin datos personales.
        token = secrets.token_urlsafe(32)
        expira = ahora + timedelta(hours=8)
        sesion = Sesion(id=token, usuario_id=usuario.id, creado_en=ahora,
                        expira_en=expira, ultima_actividad_en=ahora)
        self._sesiones.guardar(sesion)
        return InicioExitoso(token=token, usuario_id=usuario.id, expira_en=expira)
