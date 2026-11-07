"""Entidades y estados del dominio, independientes de HTTP y BD."""
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID


class EstadoCuenta(StrEnum):
    ACTIVA = "ACTIVA"
    NO_EXISTE = "NO EXISTE"  # Resultado de búsqueda: nunca se guarda en Usuario.


class EstadoSesion(StrEnum):
    VIGENTE = "VIGENTE"
    EXPIRADA = "EXPIRADA"


def _utc_aware(value: datetime) -> bool:
    return value.tzinfo is not None and value.utcoffset() is not None


@dataclass(frozen=True, slots=True)
class Usuario:
    id: UUID
    nombre: str
    email_normalizado: str
    creado_en: datetime
    estado: EstadoCuenta = EstadoCuenta.ACTIVA
    rol: str = "CLIENTE"

    def __post_init__(self) -> None:
        if self.estado is not EstadoCuenta.ACTIVA:
            raise ValueError("Un usuario persistido debe tener estado ACTIVA")
        if not self.nombre.strip() or not self.email_normalizado.strip():
            raise ValueError("Nombre y correo son obligatorios")
        if not _utc_aware(self.creado_en):
            raise ValueError("creado_en requiere zona horaria")


@dataclass(frozen=True, slots=True)
class Empresa:
    id: UUID
    usuario_id: UUID
    nombre: str
    ciudad: str
    creado_en: datetime
    nit: str | None = None
    sector: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.id, UUID) or not isinstance(self.usuario_id, UUID):
            raise ValueError("Los identificadores de empresa y usuario deben ser UUID")
        for campo, limite, obligatorio in (
            ("nombre", 150, True), ("ciudad", 100, True),
            ("nit", 20, False), ("sector", 100, False),
        ):
            valor = getattr(self, campo)
            if valor is None and not obligatorio:
                continue
            if not isinstance(valor, str):
                raise ValueError(f"{campo} debe ser texto")
            valor = valor.strip()
            if obligatorio and not valor:
                raise ValueError(f"{campo} es obligatorio")
            if len(valor) > limite:
                raise ValueError(f"{campo} admite máximo {limite} caracteres")
            object.__setattr__(self, campo, valor if obligatorio else valor or None)
        if not isinstance(self.creado_en, datetime) or not _utc_aware(self.creado_en):
            raise ValueError("creado_en requiere zona horaria")
        object.__setattr__(self, "creado_en", self.creado_en.astimezone(timezone.utc))


@dataclass(frozen=True, slots=True)
class Credencial:
    usuario_id: UUID
    password_hash: str

    def __post_init__(self) -> None:
        if not self.password_hash:
            raise ValueError("El hash no puede estar vacío")


@dataclass(frozen=True, slots=True)
class Sesion:
    id: str
    usuario_id: UUID
    creado_en: datetime
    expira_en: datetime
    ultima_actividad_en: datetime

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Identificador de sesión requerido")
        if not all(_utc_aware(d) for d in (self.creado_en, self.expira_en, self.ultima_actividad_en)):
            raise ValueError("Las fechas requieren zona horaria")
        if self.expira_en <= self.creado_en:
            raise ValueError("La expiración debe ser posterior a la creación")
        if not self.creado_en <= self.ultima_actividad_en <= self.expira_en:
            raise ValueError("Última actividad fuera de vigencia")

    def estado_en(self, ahora: datetime) -> EstadoSesion:
        if not _utc_aware(ahora):
            raise ValueError("ahora requiere zona horaria")
        return EstadoSesion.VIGENTE if ahora < self.expira_en else EstadoSesion.EXPIRADA
