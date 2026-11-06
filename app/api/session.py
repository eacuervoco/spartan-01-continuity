"""Adaptación HTTP para sesiones y protección CSRF."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel

from app.core.session_service import SessionService, SesionNoVigente

from app.api.origin import verificar_origen

router = APIRouter(prefix="/auth", tags=["Sesiones"])
COOKIE = "continuity_session"


def usuario_autenticado(request: Request) -> UUID:
    token = request.cookies.get(COOKIE)
    try:
        return request.app.state.session_service.autenticar(token)
    except SesionNoVigente as exc:
        raise HTTPException(status_code=401, detail="Sesión no vigente") from exc


class SesionActual(BaseModel):
    usuario_id: UUID
    estado_sesion: str = "VIGENTE"


@router.get("/session", response_model=SesionActual)
def consultar_sesion(usuario_id: UUID = Depends(usuario_autenticado)) -> SesionActual:
    return SesionActual(usuario_id=usuario_id)


class TokenCsrf(BaseModel):
    csrf_token: str


@router.get("/csrf", response_model=TokenCsrf)
def consultar_csrf(request: Request, _: UUID = Depends(usuario_autenticado)) -> TokenCsrf:
    return TokenCsrf(csrf_token=request.app.state.csrf.token(request.cookies[COOKIE]))


class LogoutSalida(BaseModel):
    mensaje: str = "Sesión cerrada"


@router.post("/logout", response_model=LogoutSalida)
def cerrar_sesion(request: Request, response: Response,
                  _: UUID = Depends(usuario_autenticado)) -> LogoutSalida:
    verificar_origen(request)
    token = request.cookies[COOKIE]
    if not request.app.state.csrf.valido(token, request.headers.get("x-csrf-token")):
        raise HTTPException(status_code=403, detail="Token CSRF inválido")
    request.app.state.session_service.cerrar(token)
    response.delete_cookie(key=COOKIE, path="/auth", httponly=True,
                           secure=request.app.state.secure_cookies, samesite="lax")
    return LogoutSalida()
