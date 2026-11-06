"""Composición explícita de las dependencias: un proceso, almacenamiento temporal."""

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.infrastructure.audit import registrar_evento
import os
from app.api.session import router as session_router
from app.api.access import router as access_router
from app.core.access_service import AccessService
from app.infrastructure.memory import NoMembershipLookup
from app.core.session_service import SessionService
from app.infrastructure.csrf import CsrfProtector
from app.api.auth import router
from app.core.registration import RegistroService
from app.infrastructure.memory import MemoryUserRepository, MemorySessionRepository
from app.core.login import LoginService
from app.infrastructure.rate_limit import MemoryLoginLimiter
from app.infrastructure.security import Argon2PasswordHasher
from app.infrastructure.postgres_connection import nueva_conexion
from app.infrastructure.postgres_users import PostgresUserRepository
from app.infrastructure.postgres_sessions import PostgresSessionRepository


def create_app() -> FastAPI:
    app = FastAPI(title="ContinuitY · RF01", version="0.6.0")
    storage = os.getenv("CONTINUITY_STORAGE", "memory").strip().lower()

    if storage == "postgres":
        app.state.usuarios = PostgresUserRepository(nueva_conexion)
        app.state.sesiones = PostgresSessionRepository(nueva_conexion)
    elif storage == "memory":
        app.state.usuarios = MemoryUserRepository()
        app.state.sesiones = MemorySessionRepository()
    else:
        raise ValueError("CONTINUITY_STORAGE inválido")

    hasher = Argon2PasswordHasher()

    app.state.registro_service = RegistroService(app.state.usuarios, hasher)
    # Hash ficticio calculado al iniciar la aplicación para mitigar enumeración por tiempo.
    app.state.login_service = LoginService(
        app.state.usuarios,
        app.state.sesiones,
        hasher,
        hasher.generar_hash("clave-ficticia-para-timing"),
    )
    app.state.login_limiter = MemoryLoginLimiter()
    app.state.session_service = SessionService(app.state.sesiones)
    app.state.csrf = CsrfProtector()
    app.state.access_service = AccessService(app.state.usuarios, NoMembershipLookup())
    app.state.secure_cookies = (
        os.getenv("CONTINUITY_ENV", "production") != "development"
    )

    @app.middleware("http")
    async def auditoria(request: Request, call_next):
        try:
            response = await call_next(request)
        except Exception:
            registrar_evento(request, 500)
            raise
        registrar_evento(request, response.status_code)
        return response

    frontend_root = Path(__file__).resolve().parent
    app.mount("/static", StaticFiles(directory=frontend_root / "static"), name="static")

    @app.get("/login", include_in_schema=False)
    def login_page() -> FileResponse:
        return FileResponse(
            frontend_root / "templates" / "login.html", media_type="text/html"
        )

    @app.get("/register", include_in_schema=False)
    def register_page() -> FileResponse:
        return FileResponse(
            frontend_root / "templates" / "register.html", media_type="text/html"
        )

    @app.get("/access", include_in_schema=False)
    def access_page() -> FileResponse:
        return FileResponse(
            frontend_root / "templates" / "access.html", media_type="text/html"
        )

    @app.get("/", include_in_schema=False)
    def home() -> RedirectResponse:
        return RedirectResponse("/login", status_code=307)

    app.include_router(router)
    app.include_router(session_router)
    app.include_router(access_router)
    return app


app = create_app()
