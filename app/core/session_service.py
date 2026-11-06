"""Ciclo de vida de sesiones: reglas independientes de HTTP."""
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from uuid import UUID
from .models import EstadoSesion, Sesion
from .repositories import SessionRepository


class SesionNoVigente(Exception):
    pass


class SessionService:
    INACTIVIDAD_MAXIMA = timedelta(minutes=30)

    def __init__(self, sesiones: SessionRepository):
        self._sesiones = sesiones

    def autenticar(self, token: str | None, ahora: datetime | None = None) -> UUID:
        ahora = ahora or datetime.now(timezone.utc)
        sesion = self._sesiones.buscar(token) if token else None
        if (sesion is None or sesion.estado_en(ahora) is EstadoSesion.EXPIRADA
                or ahora >= sesion.ultima_actividad_en + self.INACTIVIDAD_MAXIMA):
            if sesion is not None:
                self._sesiones.invalidar(sesion.id)
            raise SesionNoVigente()
        # La duración absoluta expira_en no cambia con cada actividad.
        self._sesiones.guardar(replace(sesion, ultima_actividad_en=max(ahora, sesion.ultima_actividad_en)))
        return sesion.usuario_id

    def cerrar(self, token: str) -> None:
        self._sesiones.invalidar(token)
