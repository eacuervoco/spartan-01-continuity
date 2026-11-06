"""Contrato HTTP del contexto del usuario autenticado."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from app.api.session import usuario_autenticado
from app.core.access_service import AccessService, UsuarioNoDisponible

router = APIRouter(prefix="/auth", tags=["Autenticación"])


class MiContexto(BaseModel):
    id: UUID
    nombre: str
    email: str
    estado: str
    rol: str
    destino: str


def obtener_acceso(request: Request) -> AccessService:
    return request.app.state.access_service


@router.get("/me", response_model=MiContexto)
def mi_contexto(usuario_id: UUID = Depends(usuario_autenticado),
               servicio: AccessService = Depends(obtener_acceso)) -> MiContexto:
    try:
        contexto = servicio.consultar(usuario_id)
    except UsuarioNoDisponible as exc:
        raise HTTPException(status_code=401, detail="Sesión no vigente") from exc
    u = contexto.usuario
    return MiContexto(id=u.id, nombre=u.nombre, email=u.email_normalizado,
                      estado=u.estado.value, rol=u.rol, destino=contexto.destino.value)
