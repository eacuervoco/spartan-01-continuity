"""Adaptación HTTP del registro; sin reglas de negocio en el endpoint."""
from dataclasses import dataclass
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from app.core.login import CredencialesInvalidas, LoginService
from app.infrastructure.rate_limit import DemasiadosIntentos, MemoryLoginLimiter
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.registration import CorreoDuplicado, RegistroInvalido, RegistroService

from app.api.origin import verificar_origen

router = APIRouter(prefix="/auth", tags=["Autenticación"], dependencies=[Depends(verificar_origen)])


class RegistroEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=12, max_length=1024)
    confirmacion_password: str


class RegistroSalida(BaseModel):
    id: UUID
    nombre: str
    email: str
    estado: str
    rol: str


def obtener_registro(request: Request) -> RegistroService:
    return request.app.state.registro_service


@router.post("/register", response_model=RegistroSalida, status_code=status.HTTP_201_CREATED)
def registrar(datos: RegistroEntrada, servicio: RegistroService = Depends(obtener_registro)) -> RegistroSalida:
    try:
        usuario = servicio.registrar(datos.nombre, str(datos.email), datos.password,
                                    datos.confirmacion_password)
    except RegistroInvalido as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except CorreoDuplicado as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        # No filtrar al cliente el detalle de fallos internos del repositorio.
        raise HTTPException(status_code=503, detail="Registro temporalmente no disponible") from exc
    return RegistroSalida(id=usuario.id, nombre=usuario.nombre,
                          email=usuario.email_normalizado,
                          estado=usuario.estado.value, rol=usuario.rol)


class LoginEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str


class LoginSalida(BaseModel):
    mensaje: str = "Autenticación exitosa"


def obtener_login(request: Request) -> LoginService:
    return request.app.state.login_service


def obtener_limitador(request: Request) -> MemoryLoginLimiter:
    return request.app.state.login_limiter


@router.post("/login", response_model=LoginSalida)
def iniciar_sesion(datos: LoginEntrada, request: Request, response: Response,
                   servicio: LoginService = Depends(obtener_login),
                   limitador: MemoryLoginLimiter = Depends(obtener_limitador)) -> LoginSalida:
    ip = request.client.host if request.client else "desconocida"
    correo = str(datos.email)
    try:
        limitador.verificar(ip, correo)
    except DemasiadosIntentos as exc:
        raise HTTPException(status_code=429, detail="Demasiados intentos. Inténtelo más tarde.",
                            headers={"Retry-After": "900"}) from exc
    try:
        resultado = servicio.iniciar(correo, datos.password)
    except CredencialesInvalidas as exc:
        limitador.fallo(ip, correo)
        raise HTTPException(status_code=401, detail="Credenciales inválidas") from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Autenticación temporalmente no disponible") from exc
    limitador.exito(ip, correo)
    # Por defecto Secure activo: en localhost HTTP se permite explícitamente modo desarrollo.
    response.set_cookie(key="continuity_session", value=resultado.token,
                        httponly=True, secure=request.app.state.secure_cookies, samesite="lax",
                        path="/auth", max_age=8 * 3600)
    return LoginSalida()
