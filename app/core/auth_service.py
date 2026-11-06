"""Servicio mínimo de consulta de estado. Registro y login pertenecen a PBI posteriores."""
from datetime import datetime
from .models import EstadoCuenta, EstadoSesion
from .repositories import SessionRepository, UserRepository


class AuthService:
    def __init__(self, usuarios: UserRepository, sesiones: SessionRepository) -> None:
        self._usuarios = usuarios
        self._sesiones = sesiones

    def estado_cuenta(self, email_normalizado: str) -> EstadoCuenta:
        return (EstadoCuenta.ACTIVA if self._usuarios.buscar_por_correo(email_normalizado)
                else EstadoCuenta.NO_EXISTE)

    def estado_sesion(self, token: str, ahora: datetime) -> EstadoSesion:
        sesion = self._sesiones.buscar(token)
        return sesion.estado_en(ahora) if sesion else EstadoSesion.EXPIRADA
