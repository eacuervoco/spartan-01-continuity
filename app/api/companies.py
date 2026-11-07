"""API RF02; reutiliza las sesiones y defensas existentes de RF01."""
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.api.origin import verificar_origen
from app.api.session import COOKIE, usuario_autenticado
from app.core.company_service import EmpresaDuplicada, EmpresaInvalida, EmpresaService


class CompanyRoute(APIRoute):
    """Controla errores solo en RF02, incluidas dependencias y respuesta."""
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handler(request: Request):
            try:
                return await original(request)
            except RequestValidationError as exc:
                # Evitar devolver el cuerpo recibido o contextos internos.
                detalle = [{"loc": e["loc"], "msg": e["msg"], "type": e["type"]}
                           for e in exc.errors()]
                raise HTTPException(status_code=422, detail=detalle) from exc
            except HTTPException:
                raise
            except Exception as exc:
                raise HTTPException(status_code=500,
                                    detail="Operación de empresa temporalmente no disponible") from exc

        return handler


router = APIRouter(prefix="/auth/companies", tags=["Empresas"], route_class=CompanyRoute)


class EmpresaEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str = Field(min_length=1, max_length=150)
    ciudad: str = Field(min_length=1, max_length=100)
    nit: str | None = Field(default=None, max_length=20)
    sector: str | None = Field(default=None, max_length=100)

    @field_validator("nombre", "ciudad", "nit", "sector", mode="before")
    @classmethod
    def normalizar(cls, valor):
        return valor.strip() if isinstance(valor, str) else valor


class EmpresaSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nombre: str
    ciudad: str
    nit: str | None
    sector: str | None
    creado_en: datetime


def obtener_empresas(request: Request) -> EmpresaService:
    return request.app.state.empresa_service


def proteger_registro(request: Request, usuario_id: UUID = Depends(usuario_autenticado)) -> UUID:
    verificar_origen(request)
    if not request.app.state.csrf.valido(request.cookies[COOKIE], request.headers.get("x-csrf-token")):
        raise HTTPException(status_code=403, detail="Token CSRF inválido")
    return usuario_id


@router.post("", response_model=EmpresaSalida, status_code=201)
def registrar_empresa(datos: EmpresaEntrada, usuario_id: UUID = Depends(proteger_registro),
                      servicio: EmpresaService = Depends(obtener_empresas)) -> EmpresaSalida:
    try:
        empresa = servicio.registrar(usuario_id, datos.nombre, datos.ciudad, datos.nit, datos.sector)
    except EmpresaInvalida as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except EmpresaDuplicada as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return EmpresaSalida.model_validate(empresa)


@router.get("/me", response_model=EmpresaSalida)
def consultar_empresa(usuario_id: UUID = Depends(usuario_autenticado),
                      servicio: EmpresaService = Depends(obtener_empresas)) -> EmpresaSalida:
    empresa = servicio.consultar(usuario_id)
    if empresa is None:
        raise HTTPException(status_code=404, detail="No tiene una empresa registrada")
    return EmpresaSalida.model_validate(empresa)
