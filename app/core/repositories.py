"""Contratos (Protocol): dominio independiente de infraestructura concreta."""
from typing import Protocol, runtime_checkable
from uuid import UUID
from .models import Credencial, Empresa, Sesion, Usuario


@runtime_checkable
class CompanyRepository(Protocol):
    def buscar_por_usuario(self, usuario_id: UUID) -> Empresa | None: ...
    def crear(self, empresa: Empresa) -> None:
        """Crear sin sobrescribir, como operación indivisible.

        Si el usuario ya tiene empresa, lanzar ValueError("Empresa duplicada")
        sin cambios, incluso ante creaciones simultáneas.
        """
        ...


@runtime_checkable
class UserRepository(Protocol):
    def buscar_por_correo(self, email_normalizado: str) -> Usuario | None: ...
    def buscar_por_id(self, usuario_id: UUID) -> Usuario | None: ...
    def buscar_credencial(self, usuario_id: UUID) -> Credencial | None: ...
    def crear_cuenta(self, usuario: Usuario, credencial: Credencial) -> None:
        """Crear ambas entidades como una operación indivisible o fallar sin cambios."""
        ...


@runtime_checkable
class SessionRepository(Protocol):
    def guardar(self, sesion: Sesion) -> None: ...
    def buscar(self, token: str) -> Sesion | None: ...
    def invalidar(self, token: str) -> None: ...


@runtime_checkable
class MembershipLookup(Protocol):
    def tiene_asociacion_autorizada(self, usuario_id: UUID) -> bool: ...


class PasswordHasher(Protocol):
    def generar_hash(self, password: str) -> str: ...
    def verificar(self, password: str, password_hash: str) -> bool: ...
