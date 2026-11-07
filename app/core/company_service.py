"""Registro y consulta de empresa sin dependencias de HTTP ni persistencia."""
from datetime import datetime, timezone
from uuid import UUID, uuid4

from .models import Empresa
from .repositories import CompanyRepository


class EmpresaDuplicada(Exception):
    pass


class EmpresaInvalida(Exception):
    pass


class EmpresaService:
    def __init__(self, empresas: CompanyRepository) -> None:
        self._empresas = empresas

    def registrar(self, usuario_id: UUID, nombre: str, ciudad: str,
                  nit: str | None = None, sector: str | None = None) -> Empresa:
        """Recibe el usuario del llamador confiable; no autentica sesiones."""
        try:
            empresa = Empresa(id=uuid4(), usuario_id=usuario_id, nombre=nombre,
                              ciudad=ciudad, nit=nit, sector=sector,
                              creado_en=datetime.now(timezone.utc))
        except ValueError as exc:
            raise EmpresaInvalida(str(exc)) from exc
        if self.consultar(usuario_id) is not None:
            raise EmpresaDuplicada("El usuario ya tiene una empresa registrada")
        try:
            self._empresas.crear(empresa)
        except ValueError as exc:
            if str(exc) == "Empresa duplicada":
                raise EmpresaDuplicada("El usuario ya tiene una empresa registrada") from exc
            raise
        return empresa

    def consultar(self, usuario_id: UUID) -> Empresa | None:
        return self._empresas.buscar_por_usuario(usuario_id)
