"""PBI-05: decisión de destino independiente de HTTP y de empresas concretas."""
from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID
from .models import Usuario
from .repositories import MembershipLookup, UserRepository


class DestinoAcceso(StrEnum):
    INCORPORACION_EMPRESARIAL = "INCORPORACION_EMPRESARIAL"
    PANEL = "PANEL"


class UsuarioNoDisponible(Exception):
    """La sesión identifica un usuario que ya no puede consultarse."""


@dataclass(frozen=True, slots=True)
class ContextoAcceso:
    usuario: Usuario
    destino: DestinoAcceso


class AccessService:
    def __init__(self, usuarios: UserRepository, membresias: MembershipLookup):
        self._usuarios = usuarios
        self._membresias = membresias

    def consultar(self, usuario_id: UUID) -> ContextoAcceso:
        usuario = self._usuarios.buscar_por_id(usuario_id)
        if usuario is None:
            raise UsuarioNoDisponible()
        # Una respuesta ausente o errónea nunca implica permiso.
        try:
            autorizada = self._membresias.tiene_asociacion_autorizada(usuario_id) is True
        except Exception:
            autorizada = False
        destino = DestinoAcceso.PANEL if autorizada else DestinoAcceso.INCORPORACION_EMPRESARIAL
        return ContextoAcceso(usuario=usuario, destino=destino)
