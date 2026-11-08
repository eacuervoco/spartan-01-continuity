# Evidencia de implementación

Base: main, 1f858c0. Extractos de archivos versionados; sin datos de ejecución. Los números corresponden a líneas originales.

## app/api/auth.py

```text
1: """Adaptación HTTP del registro; sin reglas de negocio en el endpoint."""
2: from dataclasses import dataclass
3: from uuid import UUID
4: 
5: from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
6: from app.core.login import CredencialesInvalidas, LoginService
7: from app.infrastructure.rate_limit import DemasiadosIntentos, MemoryLoginLimiter
8: from pydantic import BaseModel, ConfigDict, EmailStr, Field
9: 
10: from app.core.registration import CorreoDuplicado, RegistroInvalido, RegistroService
11: 
12: from app.api.origin import verificar_origen
13: 
14: router = APIRouter(prefix="/auth", tags=["Autenticación"], dependencies=[Depends(verificar_origen)])
15: 
16: 
17: class RegistroEntrada(BaseModel):
18:     model_config = ConfigDict(extra="forbid")
19:     nombre: str = Field(min_length=1, max_length=120)
20:     email: EmailStr
21:     password: str = Field(min_length=12, max_length=1024)
22:     confirmacion_password: str
23: 
24: 
25: class RegistroSalida(BaseModel):
26:     id: UUID
27:     nombre: str
28:     email: str
29:     estado: str
30:     rol: str
31: 
32: 
33: def obtener_registro(request: Request) -> RegistroService:
34:     return request.app.state.registro_service
35: 
36: 
37: @router.post("/register", response_model=RegistroSalida, status_code=status.HTTP_201_CREATED)
38: def registrar(datos: RegistroEntrada, servicio: RegistroService = Depends(obtener_registro)) -> RegistroSalida:
39:     try:
40:         usuario = servicio.registrar(datos.nombre, str(datos.email), datos.password,
41:                                     datos.confirmacion_password)
42:     except RegistroInvalido as exc:
43:         raise HTTPException(status_code=422, detail=str(exc)) from exc
44:     except CorreoDuplicado as exc:
45:         raise HTTPException(status_code=409, detail=str(exc)) from exc
46:     except Exception as exc:
47:         # No filtrar al cliente el detalle de fallos internos del repositorio.
48:         raise HTTPException(status_code=503, detail="Registro temporalmente no disponible") from exc
49:     return RegistroSalida(id=usuario.id, nombre=usuario.nombre,
50:                           email=usuario.email_normalizado,
51:                           estado=usuario.estado.value, rol=usuario.rol)
52: 
53: 
54: class LoginEntrada(BaseModel):
55:     model_config = ConfigDict(extra="forbid")
56:     email: EmailStr
57:     password: str
58: 
59: 
60: class LoginSalida(BaseModel):
61:     mensaje: str = "Autenticación exitosa"
62: 
63: 
64: def obtener_login(request: Request) -> LoginService:
65:     return request.app.state.login_service
66: 
67: 
68: def obtener_limitador(request: Request) -> MemoryLoginLimiter:
69:     return request.app.state.login_limiter
70: 
71: 
72: @router.post("/login", response_model=LoginSalida)
73: def iniciar_sesion(datos: LoginEntrada, request: Request, response: Response,
74:                    servicio: LoginService = Depends(obtener_login),
75:                    limitador: MemoryLoginLimiter = Depends(obtener_limitador)) -> LoginSalida:
76:     ip = request.client.host if request.client else "desconocida"
77:     correo = str(datos.email)
78:     try:
79:         limitador.verificar(ip, correo)
80:     except DemasiadosIntentos as exc:
81:         raise HTTPException(status_code=429, detail="Demasiados intentos. Inténtelo más tarde.",
82:                             headers={"Retry-After": "900"}) from exc
83:     try:
84:         resultado = servicio.iniciar(correo, datos.password)
85:     except CredencialesInvalidas as exc:
86:         limitador.fallo(ip, correo)
87:         raise HTTPException(status_code=401, detail="Credenciales inválidas") from exc
88:     except Exception as exc:
89:         raise HTTPException(status_code=503, detail="Autenticación temporalmente no disponible") from exc
90:     limitador.exito(ip, correo)
91:     # Por defecto Secure activo: en localhost HTTP se permite explícitamente modo desarrollo.
92:     response.set_cookie(key="continuity_session", value=resultado.token,
93:                         httponly=True, secure=request.app.state.secure_cookies, samesite="lax",
94:                         path="/auth", max_age=8 * 3600)
95:     return LoginSalida()
```

## app/api/session.py

```text
1: """Adaptación HTTP para sesiones y protección CSRF."""
2: from uuid import UUID
3: from fastapi import APIRouter, Depends, HTTPException, Request, Response
4: from pydantic import BaseModel
5: 
6: from app.core.session_service import SessionService, SesionNoVigente
7: 
8: from app.api.origin import verificar_origen
9: 
10: router = APIRouter(prefix="/auth", tags=["Sesiones"])
11: COOKIE = "continuity_session"
12: 
13: 
14: def usuario_autenticado(request: Request) -> UUID:
15:     token = request.cookies.get(COOKIE)
16:     try:
17:         return request.app.state.session_service.autenticar(token)
18:     except SesionNoVigente as exc:
19:         raise HTTPException(status_code=401, detail="Sesión no vigente") from exc
20: 
21: 
22: class SesionActual(BaseModel):
23:     usuario_id: UUID
24:     estado_sesion: str = "VIGENTE"
25: 
26: 
27: @router.get("/session", response_model=SesionActual)
28: def consultar_sesion(usuario_id: UUID = Depends(usuario_autenticado)) -> SesionActual:
29:     return SesionActual(usuario_id=usuario_id)
30: 
31: 
32: class TokenCsrf(BaseModel):
33:     csrf_token: str
34: 
35: 
36: @router.get("/csrf", response_model=TokenCsrf)
37: def consultar_csrf(request: Request, _: UUID = Depends(usuario_autenticado)) -> TokenCsrf:
38:     return TokenCsrf(csrf_token=request.app.state.csrf.token(request.cookies[COOKIE]))
39: 
40: 
41: class LogoutSalida(BaseModel):
42:     mensaje: str = "Sesión cerrada"
43: 
44: 
45: @router.post("/logout", response_model=LogoutSalida)
46: def cerrar_sesion(request: Request, response: Response,
47:                   _: UUID = Depends(usuario_autenticado)) -> LogoutSalida:
48:     verificar_origen(request)
49:     token = request.cookies[COOKIE]
50:     if not request.app.state.csrf.valido(token, request.headers.get("x-csrf-token")):
51:         raise HTTPException(status_code=403, detail="Token CSRF inválido")
52:     request.app.state.session_service.cerrar(token)
53:     response.delete_cookie(key=COOKIE, path="/auth", httponly=True,
54:                            secure=request.app.state.secure_cookies, samesite="lax")
55:     return LogoutSalida()
```

## app/api/origin.py

```text
1: """Defensa básica frente a solicitudes cross-site que cambian estado."""
2: from urllib.parse import urlsplit
3: from fastapi import HTTPException, Request
4: 
5: 
6: def verificar_origen(request: Request) -> None:
7:     if request.headers.get("sec-fetch-site", "").lower() == "cross-site":
8:         raise HTTPException(status_code=403, detail="Origen no autorizado")
9:     origin = request.headers.get("origin")
10:     if origin:
11:         parsed = urlsplit(origin)
12:         expected = urlsplit(str(request.base_url))
13:         if parsed.scheme not in ("http", "https") or (parsed.scheme, parsed.netloc) != (expected.scheme, expected.netloc):
14:             raise HTTPException(status_code=403, detail="Origen no autorizado")
```

## app/api/companies.py

```text
1: """API RF02; reutiliza las sesiones y defensas existentes de RF01."""
2: from datetime import datetime
3: from uuid import UUID
4: 
5: from fastapi import APIRouter, Depends, HTTPException, Request
6: from fastapi.exceptions import RequestValidationError
7: from fastapi.routing import APIRoute
8: from pydantic import BaseModel, ConfigDict, Field, field_validator
9: 
10: from app.api.origin import verificar_origen
11: from app.api.session import COOKIE, usuario_autenticado
12: from app.core.company_service import EmpresaDuplicada, EmpresaInvalida, EmpresaService
13: 
14: 
15: class CompanyRoute(APIRoute):
16:     """Controla errores solo en RF02, incluidas dependencias y respuesta."""
17:     def get_route_handler(self):
18:         original = super().get_route_handler()
19: 
20:         async def handler(request: Request):
21:             try:
22:                 return await original(request)
23:             except RequestValidationError as exc:
24:                 # Evitar devolver el cuerpo recibido o contextos internos.
25:                 detalle = [{"loc": e["loc"], "msg": e["msg"], "type": e["type"]}
26:                            for e in exc.errors()]
27:                 raise HTTPException(status_code=422, detail=detalle) from exc
28:             except HTTPException:
29:                 raise
30:             except Exception as exc:
31:                 raise HTTPException(status_code=500,
32:                                     detail="Operación de empresa temporalmente no disponible") from exc
33: 
34:         return handler
35: 
36: 
37: router = APIRouter(prefix="/auth/companies", tags=["Empresas"], route_class=CompanyRoute)
38: 
39: 
40: class EmpresaEntrada(BaseModel):
41:     model_config = ConfigDict(extra="forbid")
42:     nombre: str = Field(min_length=1, max_length=150)
43:     ciudad: str = Field(min_length=1, max_length=100)
44:     nit: str | None = Field(default=None, max_length=20)
45:     sector: str | None = Field(default=None, max_length=100)
46: 
47:     @field_validator("nombre", "ciudad", "nit", "sector", mode="before")
48:     @classmethod
49:     def normalizar(cls, valor):
50:         return valor.strip() if isinstance(valor, str) else valor
51: 
52: 
53: class EmpresaSalida(BaseModel):
54:     model_config = ConfigDict(from_attributes=True)
55:     id: UUID
56:     nombre: str
57:     ciudad: str
58:     nit: str | None
59:     sector: str | None
60:     creado_en: datetime
61: 
62: 
63: def obtener_empresas(request: Request) -> EmpresaService:
64:     return request.app.state.empresa_service
65: 
66: 
67: def proteger_registro(request: Request, usuario_id: UUID = Depends(usuario_autenticado)) -> UUID:
68:     verificar_origen(request)
69:     if not request.app.state.csrf.valido(request.cookies[COOKIE], request.headers.get("x-csrf-token")):
70:         raise HTTPException(status_code=403, detail="Token CSRF inválido")
71:     return usuario_id
72: 
73: 
74: @router.post("", response_model=EmpresaSalida, status_code=201)
75: def registrar_empresa(datos: EmpresaEntrada, usuario_id: UUID = Depends(proteger_registro),
76:                       servicio: EmpresaService = Depends(obtener_empresas)) -> EmpresaSalida:
77:     try:
78:         empresa = servicio.registrar(usuario_id, datos.nombre, datos.ciudad, datos.nit, datos.sector)
79:     except EmpresaInvalida as exc:
80:         raise HTTPException(status_code=422, detail=str(exc)) from exc
81:     except EmpresaDuplicada as exc:
82:         raise HTTPException(status_code=409, detail=str(exc)) from exc
83:     return EmpresaSalida.model_validate(empresa)
84: 
85: 
86: @router.get("/me", response_model=EmpresaSalida)
87: def consultar_empresa(usuario_id: UUID = Depends(usuario_autenticado),
88:                       servicio: EmpresaService = Depends(obtener_empresas)) -> EmpresaSalida:
89:     empresa = servicio.consultar(usuario_id)
90:     if empresa is None:
91:         raise HTTPException(status_code=404, detail="No tiene una empresa registrada")
92:     return EmpresaSalida.model_validate(empresa)
```

## app/core/registration.py

```text
1: """Reglas de registro: independientes del transporte HTTP."""
2: from datetime import datetime, timezone
3: from uuid import uuid4
4: 
5: from .models import Credencial, Usuario
6: from .repositories import PasswordHasher, UserRepository
7: 
8: 
9: class CorreoDuplicado(Exception):
10:     pass
11: 
12: 
13: class RegistroInvalido(Exception):
14:     pass
15: 
16: 
17: class RegistroService:
18:     def __init__(self, usuarios: UserRepository, hasher: PasswordHasher) -> None:
19:         self._usuarios = usuarios
20:         self._hasher = hasher
21: 
22:     def registrar(self, nombre: str, correo: str, password: str, confirmacion: str) -> Usuario:
23:         nombre = nombre.strip()
24:         correo = correo.strip().casefold()
25:         if not nombre or not correo or len(password) < 12 or password != confirmacion:
26:             raise RegistroInvalido("Datos de registro inválidos")
27:         if self._usuarios.buscar_por_correo(correo) is not None:
28:             raise CorreoDuplicado("El correo ya está registrado")
29:         usuario = Usuario(id=uuid4(), nombre=nombre, email_normalizado=correo,
30:                           creado_en=datetime.now(timezone.utc))
31:         credencial = Credencial(usuario_id=usuario.id,
32:                                 password_hash=self._hasher.generar_hash(password))
33:         try:
34:             self._usuarios.crear_cuenta(usuario, credencial)
35:         except ValueError as exc:
36:             if str(exc) == "Cuenta duplicada":
37:                 raise CorreoDuplicado("El correo ya está registrado") from exc
38:             raise
39:         return usuario
```

## app/core/login.py

```text
1: """Autenticación: no depende de FastAPI, cookies ni almacenamiento concreto."""
2: from dataclasses import dataclass
3: from datetime import datetime, timedelta, timezone
4: import secrets
5: from uuid import UUID
6: 
7: from .models import Sesion
8: from .repositories import PasswordHasher, SessionRepository, UserRepository
9: 
10: 
11: class CredencialesInvalidas(Exception):
12:     pass
13: 
14: 
15: @dataclass(frozen=True, slots=True)
16: class InicioExitoso:
17:     token: str
18:     usuario_id: UUID
19:     expira_en: datetime
20: 
21: 
22: class LoginService:
23:     def __init__(self, usuarios: UserRepository, sesiones: SessionRepository,
24:                  hasher: PasswordHasher, hash_ficticio: str) -> None:
25:         self._usuarios = usuarios
26:         self._sesiones = sesiones
27:         self._hasher = hasher
28:         self._hash_ficticio = hash_ficticio
29: 
30:     def iniciar(self, correo: str, password: str) -> InicioExitoso:
31:         normalizado = correo.strip().casefold()
32:         usuario = self._usuarios.buscar_por_correo(normalizado)
33:         credencial = self._usuarios.buscar_credencial(usuario.id) if usuario else None
34:         hash_a_verificar = credencial.password_hash if credencial else self._hash_ficticio
35:         valido = self._hasher.verificar(password, hash_a_verificar)
36:         if not usuario or not credencial or not valido:
37:             raise CredencialesInvalidas()
38:         ahora = datetime.now(timezone.utc)
39:         # 256 bits de entropía, opaco y sin datos personales.
40:         token = secrets.token_urlsafe(32)
41:         expira = ahora + timedelta(hours=8)
42:         sesion = Sesion(id=token, usuario_id=usuario.id, creado_en=ahora,
43:                         expira_en=expira, ultima_actividad_en=ahora)
44:         self._sesiones.guardar(sesion)
45:         return InicioExitoso(token=token, usuario_id=usuario.id, expira_en=expira)
```

## app/core/session_service.py

```text
1: """Ciclo de vida de sesiones: reglas independientes de HTTP."""
2: from dataclasses import replace
3: from datetime import datetime, timedelta, timezone
4: from uuid import UUID
5: from .models import EstadoSesion, Sesion
6: from .repositories import SessionRepository
7: 
8: 
9: class SesionNoVigente(Exception):
10:     pass
11: 
12: 
13: class SessionService:
14:     INACTIVIDAD_MAXIMA = timedelta(minutes=30)
15: 
16:     def __init__(self, sesiones: SessionRepository):
17:         self._sesiones = sesiones
18: 
19:     def autenticar(self, token: str | None, ahora: datetime | None = None) -> UUID:
20:         ahora = ahora or datetime.now(timezone.utc)
21:         sesion = self._sesiones.buscar(token) if token else None
22:         if (sesion is None or sesion.estado_en(ahora) is EstadoSesion.EXPIRADA
23:                 or ahora >= sesion.ultima_actividad_en + self.INACTIVIDAD_MAXIMA):
24:             if sesion is not None:
25:                 self._sesiones.invalidar(sesion.id)
26:             raise SesionNoVigente()
27:         # La duración absoluta expira_en no cambia con cada actividad.
28:         self._sesiones.guardar(replace(sesion, ultima_actividad_en=max(ahora, sesion.ultima_actividad_en)))
29:         return sesion.usuario_id
30: 
31:     def cerrar(self, token: str) -> None:
32:         self._sesiones.invalidar(token)
```

## app/core/company_service.py

```text
1: """Registro y consulta de empresa sin dependencias de HTTP ni persistencia."""
2: from datetime import datetime, timezone
3: from uuid import UUID, uuid4
4: 
5: from .models import Empresa
6: from .repositories import CompanyRepository
7: 
8: 
9: class EmpresaDuplicada(Exception):
10:     pass
11: 
12: 
13: class EmpresaInvalida(Exception):
14:     pass
15: 
16: 
17: class EmpresaService:
18:     def __init__(self, empresas: CompanyRepository) -> None:
19:         self._empresas = empresas
20: 
21:     def registrar(self, usuario_id: UUID, nombre: str, ciudad: str,
22:                   nit: str | None = None, sector: str | None = None) -> Empresa:
23:         """Recibe el usuario del llamador confiable; no autentica sesiones."""
24:         try:
25:             empresa = Empresa(id=uuid4(), usuario_id=usuario_id, nombre=nombre,
26:                               ciudad=ciudad, nit=nit, sector=sector,
27:                               creado_en=datetime.now(timezone.utc))
28:         except ValueError as exc:
29:             raise EmpresaInvalida(str(exc)) from exc
30:         if self.consultar(usuario_id) is not None:
31:             raise EmpresaDuplicada("El usuario ya tiene una empresa registrada")
32:         try:
33:             self._empresas.crear(empresa)
34:         except ValueError as exc:
35:             if str(exc) == "Empresa duplicada":
36:                 raise EmpresaDuplicada("El usuario ya tiene una empresa registrada") from exc
37:             raise
38:         return empresa
39: 
40:     def consultar(self, usuario_id: UUID) -> Empresa | None:
41:         return self._empresas.buscar_por_usuario(usuario_id)
```

## app/core/access_service.py

```text
1: """PBI-05: decisión de destino independiente de HTTP y de empresas concretas."""
2: from dataclasses import dataclass
3: from enum import StrEnum
4: from uuid import UUID
5: from .models import Usuario
6: from .repositories import MembershipLookup, UserRepository
7: 
8: 
9: class DestinoAcceso(StrEnum):
10:     INCORPORACION_EMPRESARIAL = "INCORPORACION_EMPRESARIAL"
11:     PANEL = "PANEL"
12: 
13: 
14: class UsuarioNoDisponible(Exception):
15:     """La sesión identifica un usuario que ya no puede consultarse."""
16: 
17: 
18: @dataclass(frozen=True, slots=True)
19: class ContextoAcceso:
20:     usuario: Usuario
21:     destino: DestinoAcceso
22: 
23: 
24: class AccessService:
25:     def __init__(self, usuarios: UserRepository, membresias: MembershipLookup):
26:         self._usuarios = usuarios
27:         self._membresias = membresias
28: 
29:     def consultar(self, usuario_id: UUID) -> ContextoAcceso:
30:         usuario = self._usuarios.buscar_por_id(usuario_id)
31:         if usuario is None:
32:             raise UsuarioNoDisponible()
33:         # Una respuesta ausente o errónea nunca implica permiso.
34:         try:
35:             autorizada = self._membresias.tiene_asociacion_autorizada(usuario_id) is True
36:         except Exception:
37:             autorizada = False
38:         destino = DestinoAcceso.PANEL if autorizada else DestinoAcceso.INCORPORACION_EMPRESARIAL
39:         return ContextoAcceso(usuario=usuario, destino=destino)
```

## app/core/models.py

```text
1: """Entidades y estados del dominio, independientes de HTTP y BD."""
2: from dataclasses import dataclass
3: from datetime import datetime, timezone
4: from enum import StrEnum
5: from uuid import UUID
6: 
7: 
8: class EstadoCuenta(StrEnum):
9:     ACTIVA = "ACTIVA"
10:     NO_EXISTE = "NO EXISTE"  # Resultado de búsqueda: nunca se guarda en Usuario.
11: 
12: 
13: class EstadoSesion(StrEnum):
14:     VIGENTE = "VIGENTE"
15:     EXPIRADA = "EXPIRADA"
16: 
17: 
18: def _utc_aware(value: datetime) -> bool:
19:     return value.tzinfo is not None and value.utcoffset() is not None
20: 
21: 
22: @dataclass(frozen=True, slots=True)
23: class Usuario:
24:     id: UUID
25:     nombre: str
26:     email_normalizado: str
27:     creado_en: datetime
28:     estado: EstadoCuenta = EstadoCuenta.ACTIVA
29:     rol: str = "CLIENTE"
30: 
31:     def __post_init__(self) -> None:
32:         if self.estado is not EstadoCuenta.ACTIVA:
33:             raise ValueError("Un usuario persistido debe tener estado ACTIVA")
34:         if not self.nombre.strip() or not self.email_normalizado.strip():
35:             raise ValueError("Nombre y correo son obligatorios")
36:         if not _utc_aware(self.creado_en):
37:             raise ValueError("creado_en requiere zona horaria")
38: 
39: 
40: @dataclass(frozen=True, slots=True)
41: class Empresa:
42:     id: UUID
43:     usuario_id: UUID
44:     nombre: str
45:     ciudad: str
46:     creado_en: datetime
47:     nit: str | None = None
48:     sector: str | None = None
49: 
50:     def __post_init__(self) -> None:
51:         if not isinstance(self.id, UUID) or not isinstance(self.usuario_id, UUID):
52:             raise ValueError("Los identificadores de empresa y usuario deben ser UUID")
53:         for campo, limite, obligatorio in (
54:             ("nombre", 150, True), ("ciudad", 100, True),
55:             ("nit", 20, False), ("sector", 100, False),
56:         ):
57:             valor = getattr(self, campo)
58:             if valor is None and not obligatorio:
59:                 continue
60:             if not isinstance(valor, str):
61:                 raise ValueError(f"{campo} debe ser texto")
62:             valor = valor.strip()
63:             if obligatorio and not valor:
64:                 raise ValueError(f"{campo} es obligatorio")
65:             if len(valor) > limite:
66:                 raise ValueError(f"{campo} admite máximo {limite} caracteres")
67:             object.__setattr__(self, campo, valor if obligatorio else valor or None)
68:         if not isinstance(self.creado_en, datetime) or not _utc_aware(self.creado_en):
69:             raise ValueError("creado_en requiere zona horaria")
70:         object.__setattr__(self, "creado_en", self.creado_en.astimezone(timezone.utc))
71: 
72: 
73: @dataclass(frozen=True, slots=True)
74: class Credencial:
75:     usuario_id: UUID
76:     password_hash: str
77: 
78:     def __post_init__(self) -> None:
79:         if not self.password_hash:
80:             raise ValueError("El hash no puede estar vacío")
81: 
82: 
83: @dataclass(frozen=True, slots=True)
84: class Sesion:
85:     id: str
86:     usuario_id: UUID
87:     creado_en: datetime
88:     expira_en: datetime
89:     ultima_actividad_en: datetime
90: 
91:     def __post_init__(self) -> None:
92:         if not self.id:
93:             raise ValueError("Identificador de sesión requerido")
94:         if not all(_utc_aware(d) for d in (self.creado_en, self.expira_en, self.ultima_actividad_en)):
95:             raise ValueError("Las fechas requieren zona horaria")
96:         if self.expira_en <= self.creado_en:
97:             raise ValueError("La expiración debe ser posterior a la creación")
98:         if not self.creado_en <= self.ultima_actividad_en <= self.expira_en:
99:             raise ValueError("Última actividad fuera de vigencia")
100: 
101:     def estado_en(self, ahora: datetime) -> EstadoSesion:
102:         if not _utc_aware(ahora):
103:             raise ValueError("ahora requiere zona horaria")
104:         return EstadoSesion.VIGENTE if ahora < self.expira_en else EstadoSesion.EXPIRADA
```

## app/infrastructure/security.py

```text
1: """Adaptador Argon2id para almacenar contraseñas de forma segura."""
2: from argon2 import PasswordHasher as Argon2Hasher
3: from argon2.low_level import Type
4: from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
5: 
6: 
7: class Argon2PasswordHasher:
8:     def __init__(self) -> None:
9:         # Parámetros explícitos para que las decisiones de costo sean auditables.
10:         self._hasher = Argon2Hasher(time_cost=3, memory_cost=65536, parallelism=4,
11:                                     hash_len=32, salt_len=16, type=Type.ID)
12: 
13:     def generar_hash(self, password: str) -> str:
14:         return self._hasher.hash(password)
15: 
16:     def verificar(self, password: str, password_hash: str) -> bool:
17:         try:
18:             return self._hasher.verify(password_hash, password)
19:         except (VerifyMismatchError, VerificationError, InvalidHashError):
20:             return False
```

## app/infrastructure/csrf.py

```text
1: """Token CSRF ligado a la sesión, con HMAC y clave efímera por proceso."""
2: import hashlib
3: import hmac
4: import secrets
5: 
6: 
7: class CsrfProtector:
8:     def __init__(self):
9:         self._clave = secrets.token_bytes(32)
10: 
11:     def token(self, session_id: str) -> str:
12:         return hmac.new(self._clave, session_id.encode(), hashlib.sha256).hexdigest()
13: 
14:     def valido(self, session_id: str, provided: str | None) -> bool:
15:         return bool(provided) and hmac.compare_digest(self.token(session_id), provided)
```

## app/infrastructure/rate_limit.py

```text
1: """Límite provisional por proceso; requiere almacenamiento compartido en producción."""
2: from collections import defaultdict, deque
3: from datetime import datetime, timedelta, timezone
4: from threading import RLock
5: 
6: 
7: class DemasiadosIntentos(Exception):
8:     pass
9: 
10: 
11: class MemoryLoginLimiter:
12:     """Cinco fallos por IP y por identidad dentro de 15 minutos; falla cerrada."""
13:     def __init__(self, max_fallos: int = 5, ventana_minutos: int = 15) -> None:
14:         self.max_fallos = max_fallos
15:         self.ventana = timedelta(minutes=ventana_minutos)
16:         self._fallos: dict[str, deque[datetime]] = defaultdict(deque)
17:         self._lock = RLock()
18: 
19:     def _limpiar(self, clave: str, ahora: datetime) -> None:
20:         cola = self._fallos[clave]
21:         while cola and cola[0] <= ahora - self.ventana:
22:             cola.popleft()
23: 
24:     def verificar(self, ip: str, correo: str) -> None:
25:         ahora = datetime.now(timezone.utc)
26:         with self._lock:
27:             for clave in (f"ip:{ip}", f"correo:{correo.strip().casefold()}"):
28:                 self._limpiar(clave, ahora)
29:                 if len(self._fallos[clave]) >= self.max_fallos:
30:                     raise DemasiadosIntentos()
31: 
32:     def fallo(self, ip: str, correo: str) -> None:
33:         ahora = datetime.now(timezone.utc)
34:         with self._lock:
35:             for clave in (f"ip:{ip}", f"correo:{correo.strip().casefold()}"):
36:                 self._limpiar(clave, ahora)
37:                 self._fallos[clave].append(ahora)
38: 
39:     def exito(self, ip: str, correo: str) -> None:
40:         # No se borran fallos de IP (evita que una cuenta válida elimine el límite).
41:         with self._lock:
42:             self._fallos.pop(f"correo:{correo.strip().casefold()}", None)
```

## app/infrastructure/postgres_users.py

```text
1: """Adaptador PostgreSQL del repositorio de usuarios de ContinuitY RF01.
2: 
3: Ubicación recomendada: app/infrastructure/postgres_users.py.
4: No altera los servicios, las rutas ni los repositorios en memoria.
5: """
6: 
7: from __future__ import annotations
8: 
9: from collections.abc import Callable
10: from uuid import UUID
11: 
12: import psycopg
13: from psycopg import Connection, errors
14: 
15: from app.core.models import Credencial, EstadoCuenta, Usuario
16: 
17: 
18: class PostgresUserRepository:
19:     """Implementa UserRepository con una conexión por operación.
20: 
21:     ``connect`` es una fábrica de conexiones configurable, permitiendo
22:     inyectar conexiones de una BD de pruebas separada.
23:     """
24: 
25:     def __init__(self, connect: Callable[[], Connection]) -> None:
26:         self._connect = connect
27: 
28:     @staticmethod
29:     def _usuario(row: tuple | None) -> Usuario | None:
30:         if row is None:
31:             return None
32:         return Usuario(
33:             id=row[0],
34:             nombre=row[1],
35:             email_normalizado=row[2],
36:             creado_en=row[3],
37:             estado=EstadoCuenta(row[4]),
38:             rol=row[5],
39:         )
40: 
41:     def buscar_por_correo(self, email_normalizado: str) -> Usuario | None:
42:         with self._connect() as conn:
43:             with conn.cursor() as cur:
44:                 cur.execute(
45:                     """SELECT id, nombre, email_normalizado, creado_en, estado, rol
46:                        FROM public.usuarios WHERE email_normalizado = %s""",
47:                     (email_normalizado,),
48:                 )
49:                 return self._usuario(cur.fetchone())
50: 
51:     def buscar_por_id(self, usuario_id: UUID) -> Usuario | None:
52:         with self._connect() as conn:
53:             with conn.cursor() as cur:
54:                 cur.execute(
55:                     """SELECT id, nombre, email_normalizado, creado_en, estado, rol
56:                        FROM public.usuarios WHERE id = %s""",
57:                     (usuario_id,),
58:                 )
59:                 return self._usuario(cur.fetchone())
60: 
61:     def buscar_credencial(self, usuario_id: UUID) -> Credencial | None:
62:         with self._connect() as conn:
63:             with conn.cursor() as cur:
64:                 cur.execute(
65:                     """SELECT usuario_id, password_hash
66:                        FROM public.credenciales WHERE usuario_id = %s""",
67:                     (usuario_id,),
68:                 )
69:                 row = cur.fetchone()
70:                 return Credencial(usuario_id=row[0], password_hash=row[1]) if row else None
71: 
72:     def crear_cuenta(self, usuario: Usuario, credencial: Credencial) -> None:
73:         if usuario.id != credencial.usuario_id:
74:             raise ValueError("La credencial no pertenece al usuario")
75: 
76:         try:
77:             # El contexto confirma la transacción solo si ambas inserciones
78:             # terminan correctamente; ante cualquier error hace ROLLBACK.
79:             with self._connect() as conn:
80:                 with conn.cursor() as cur:
81:                     cur.execute(
82:                         """INSERT INTO public.usuarios
83:                            (id, nombre, email_normalizado, creado_en, estado, rol)
84:                            VALUES (%s, %s, %s, %s, %s, %s)""",
85:                         (
86:                             usuario.id,
87:                             usuario.nombre,
88:                             usuario.email_normalizado,
89:                             usuario.creado_en,
90:                             usuario.estado.value,
91:                             usuario.rol,
92:                         ),
93:                     )
94:                     cur.execute(
95:                         """INSERT INTO public.credenciales
96:                            (usuario_id, password_hash) VALUES (%s, %s)""",
97:                         (credencial.usuario_id, credencial.password_hash),
98:                     )
99:         except errors.UniqueViolation as exc:
100:             # Contrato que RegistroService ya traduce a CorreoDuplicado.
101:             # No exponer valores o detalles internos del motor.
102:             raise ValueError("Cuenta duplicada") from exc
```

## app/infrastructure/postgres_sessions.py

```text
1: """Repositorio de sesiones PostgreSQL para ContinuitY RF01 (Psycopg 3).
2: 
3: Requiere database/003_sesiones_revocacion.sql.
4: No persiste tokens en claro: solo SHA-256. Mantiene tombstones para
5: que una sesión revocada no vuelva a autorizarse con un UPSERT concurrente.
6: """
7: from __future__ import annotations
8: 
9: from collections.abc import Callable
10: from datetime import datetime, timezone
11: from hashlib import sha256
12: 
13: from psycopg import Connection
14: 
15: from app.core.models import Sesion
16: from app.core.session_service import SesionNoVigente
17: 
18: 
19: class PostgresSessionRepository:
20:     def __init__(self, connect: Callable[[], Connection]) -> None:
21:         self._connect = connect
22: 
23:     @staticmethod
24:     def _digest(token: str) -> str:
25:         return sha256(token.encode("utf-8")).hexdigest()
26: 
27:     def guardar(self, sesion: Sesion) -> None:
28:         digest = self._digest(sesion.id)
29:         with self._connect() as conn:
30:             with conn.cursor() as cur:
31:                 # Si ya existe, solo actualiza la actividad. Una fila revocada
32:                 # permanece revocada y jamás es reinsertada por un UPSERT.
33:                 cur.execute(
34:                     """INSERT INTO public.sesiones
35:                        (token_digest, usuario_id, creado_en, expira_en, ultima_actividad_en)
36:                        VALUES (%s, %s, %s, %s, %s)
37:                        ON CONFLICT (token_digest) DO UPDATE
38:                        SET ultima_actividad_en = GREATEST(
39:                            sesiones.ultima_actividad_en, EXCLUDED.ultima_actividad_en
40:                        )
41:                        WHERE sesiones.revocada_en IS NULL
42:                          AND sesiones.usuario_id = EXCLUDED.usuario_id
43:                          AND sesiones.creado_en = EXCLUDED.creado_en
44:                          AND sesiones.expira_en = EXCLUDED.expira_en
45:                        RETURNING token_digest""",
46:                     (digest, sesion.usuario_id, sesion.creado_en,
47:                      sesion.expira_en, sesion.ultima_actividad_en),
48:                 )
49:                 if cur.fetchone() is None:
50:                     raise SesionNoVigente()
51: 
52:     def buscar(self, token: str) -> Sesion | None:
53:         with self._connect() as conn:
54:             with conn.cursor() as cur:
55:                 cur.execute(
56:                     """SELECT usuario_id, creado_en, expira_en, ultima_actividad_en
57:                        FROM public.sesiones
58:                        WHERE token_digest = %s AND revocada_en IS NULL""",
59:                     (self._digest(token),),
60:                 )
61:                 row = cur.fetchone()
62:         if row is None:
63:             return None
64:         return Sesion(
65:             id=token, usuario_id=row[0], creado_en=row[1],
66:             expira_en=row[2], ultima_actividad_en=row[3],
67:         )
68: 
69:     def invalidar(self, token: str) -> None:
70:         with self._connect() as conn:
71:             with conn.cursor() as cur:
72:                 cur.execute(
73:                     """UPDATE public.sesiones SET revocada_en = %s
74:                        WHERE token_digest = %s AND revocada_en IS NULL""",
75:                     (datetime.now(timezone.utc), self._digest(token)),
76:                 )
```

## app/infrastructure/postgres_companies.py

```text
1: """Repositorio RF02: conexión por operación y transacciones Psycopg existentes."""
2: from collections.abc import Callable
3: from uuid import UUID
4: 
5: from psycopg import Connection, errors
6: 
7: from app.core.models import Empresa
8: 
9: 
10: class PostgresCompanyRepository:
11:     def __init__(self, connect: Callable[[], Connection]) -> None:
12:         self._connect = connect
13: 
14:     def buscar_por_usuario(self, usuario_id: UUID) -> Empresa | None:
15:         with self._connect() as conn:
16:             with conn.cursor() as cur:
17:                 cur.execute(
18:                     """SELECT id, usuario_id, nombre, ciudad, creado_en, nit, sector
19:                        FROM public.empresas WHERE usuario_id = %s""",
20:                     (usuario_id,),
21:                 )
22:                 row = cur.fetchone()
23:         return Empresa(*row) if row is not None else None
24: 
25:     def crear(self, empresa: Empresa) -> None:
26:         try:
27:             with self._connect() as conn:
28:                 with conn.cursor() as cur:
29:                     cur.execute(
30:                         """INSERT INTO public.empresas
31:                            (id, usuario_id, nombre, ciudad, creado_en, nit, sector)
32:                            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
33:                         (empresa.id, empresa.usuario_id, empresa.nombre, empresa.ciudad,
34:                          empresa.creado_en, empresa.nit, empresa.sector),
35:                     )
36:         except errors.UniqueViolation as exc:
37:             if (exc.diag.constraint_name == "empresas_usuario_id_key"
38:                     and exc.diag.table_name == "empresas"
39:                     and exc.diag.schema_name == "public"):
40:                 raise ValueError("Empresa duplicada") from exc
41:             raise
```

## database/001_schema.sql

```text
1: -- ContinuitY RF01 - BD-02 - esquema inicial v1.0
2: -- Aplicar explícitamente en continuity_db con rol administrador/migrador.
3: -- No ejecutar desde el arranque de FastAPI.
4: BEGIN;
5: 
6: CREATE TABLE public.usuarios (
7:     id UUID PRIMARY KEY,
8:     nombre VARCHAR(120) NOT NULL CHECK (length(btrim(nombre)) > 0),
9:     email_normalizado TEXT NOT NULL UNIQUE
10:         CHECK (length(btrim(email_normalizado)) > 0 AND email_normalizado = lower(btrim(email_normalizado))),
11:     creado_en TIMESTAMPTZ NOT NULL,
12:     estado TEXT NOT NULL DEFAULT 'ACTIVA' CHECK (estado = 'ACTIVA'),
13:     rol TEXT NOT NULL DEFAULT 'CLIENTE' CHECK (rol = 'CLIENTE')
14: );
15: 
16: CREATE TABLE public.credenciales (
17:     usuario_id UUID PRIMARY KEY REFERENCES public.usuarios(id) ON DELETE CASCADE,
18:     password_hash TEXT NOT NULL CHECK (length(password_hash) > 0)
19: );
20: 
21: CREATE TABLE public.sesiones (
22:     token_digest CHAR(64) PRIMARY KEY CHECK (token_digest ~ '^[0-9a-f]{64}$'),
23:     usuario_id UUID NOT NULL REFERENCES public.usuarios(id) ON DELETE CASCADE,
24:     creado_en TIMESTAMPTZ NOT NULL,
25:     expira_en TIMESTAMPTZ NOT NULL,
26:     ultima_actividad_en TIMESTAMPTZ NOT NULL,
27:     CONSTRAINT sesiones_fechas_validas CHECK (
28:         expira_en > creado_en
29:         AND ultima_actividad_en >= creado_en
30:         AND ultima_actividad_en <= expira_en
31:     )
32: );
33: 
34: CREATE INDEX idx_sesiones_usuario ON public.sesiones(usuario_id);
35: 
36: COMMIT;
```

## database/002_permisos.sql

```text
1: -- ContinuitY RF01 - permisos de aplicacion (ejecucion separada, rol administrador)
2: -- Ejecutar DESPUES de 001_schema.sql y verificar propietarios/roles reales.
3: -- Las sentencias no revocan permisos existentes ni crean usuarios.
4: GRANT USAGE ON SCHEMA public TO continuity_app;
5: GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.usuarios, public.credenciales, public.sesiones TO continuity_app;
6: -- En un endurecimiento posterior revisar REVOKE CREATE ON SCHEMA public FROM continuity_app.
```

## database/003_sesiones_revocacion.sql

```text
1: -- BD-04: revocación irreversible de sesiones; compatible con tablas existentes.
2: -- Ejecutar solo tras revisión, con spartan_admin, en BD de pruebas primero.
3: BEGIN;
4: ALTER TABLE public.sesiones
5:     ADD COLUMN IF NOT EXISTS revocada_en TIMESTAMPTZ;
6: COMMIT;
```

## database/004_empresas.sql

```text
1: -- RF02 Bloque 2: ejecutar explícitamente con rol administrador/migrador.
2: -- Revisar y aprobar el destino antes de aplicar. No ejecutar desde FastAPI.
3: BEGIN;
4: 
5: CREATE TABLE public.empresas (
6:     id UUID PRIMARY KEY,
7:     usuario_id UUID NOT NULL
8:         REFERENCES public.usuarios(id) ON DELETE RESTRICT,
9:     nombre VARCHAR(150) NOT NULL
10:         CHECK (length(btrim(nombre)) > 0),
11:     nit VARCHAR(20),
12:     ciudad VARCHAR(100) NOT NULL
13:         CHECK (length(btrim(ciudad)) > 0),
14:     sector VARCHAR(100),
15:     creado_en TIMESTAMPTZ NOT NULL,
16:     CONSTRAINT empresas_usuario_id_key UNIQUE (usuario_id)
17: );
18: 
19: GRANT USAGE ON SCHEMA public TO continuity_app;
20: GRANT SELECT, INSERT ON TABLE public.empresas TO continuity_app;
21: 
22: COMMIT;
```
