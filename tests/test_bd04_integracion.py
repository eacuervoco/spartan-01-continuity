"""Prueba aislada BD-04; ejecutar directamente con PYTHONPATH=. ."""
from __future__ import annotations

import getpass
import os
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import psycopg

from app.core.models import Sesion
from app.core.session_service import SessionService, SesionNoVigente
from app.infrastructure.postgres_sessions import PostgresSessionRepository
from app.infrastructure.postgres_users import PostgresUserRepository
from app.core.registration import RegistroService
from app.infrastructure.security import Argon2PasswordHasher


def main() -> None:
    dbname = os.getenv("CONTINUITY_TEST_DB_NAME", "continuity_rf01_test")
    if dbname != "continuity_rf01_test":
        raise SystemExit("SEGURIDAD: solo continuity_rf01_test")
    password = os.getenv("CONTINUITY_TEST_DB_PASSWORD") or getpass.getpass(
        "Contraseña continuity_app (BD de pruebas): "
    )
    settings = dict(host="127.0.0.1", port=15432, dbname=dbname,
                    user="continuity_app", password=password, connect_timeout=5)

    def connect():
        return psycopg.connect(**settings)

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user")
            assert cur.fetchone() == ("continuity_rf01_test", "continuity_app")
            cur.execute("""SELECT 1 FROM information_schema.columns
                           WHERE table_schema='public' AND table_name='sesiones'
                           AND column_name='revocada_en'""")
            assert cur.fetchone(), "Aplicar migración 003 en BD de pruebas"
    print("[OK] Destino de prueba y migración 003")

    users = PostgresUserRepository(connect)
    usuario = RegistroService(users, Argon2PasswordHasher()).registrar(
        "Prueba BD04", f"bd04-{uuid4().hex}@example.test", "ClaveRF01!2026_Prueba",
        "ClaveRF01!2026_Prueba"
    )
    repo = PostgresSessionRepository(connect)
    service = SessionService(repo)
    ahora = datetime.now(timezone.utc)
    token = secrets.token_urlsafe(32)
    sesion = Sesion(id=token, usuario_id=usuario.id, creado_en=ahora,
                    expira_en=ahora + timedelta(hours=8), ultima_actividad_en=ahora)
    repo.guardar(sesion)
    assert PostgresSessionRepository(connect).buscar(token) == sesion
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT token_digest FROM public.sesiones WHERE usuario_id = %s", (usuario.id,))
            digest = cur.fetchone()[0].strip()
            assert digest != token and len(digest) == 64
    print("[OK] Creación, lectura tras reconexión y token no almacenado en claro")

    proxima = ahora + timedelta(minutes=5)
    assert service.autenticar(token, ahora=proxima) == usuario.id
    assert repo.buscar(token).ultima_actividad_en == proxima
    assert repo.buscar(token).expira_en == sesion.expira_en
    print("[OK] Actualización de actividad sin alterar expiración absoluta")

    service.cerrar(token)
    assert repo.buscar(token) is None
    try:
        repo.guardar(sesion)
    except SesionNoVigente:
        pass
    else:
        raise AssertionError("Una sesión revocada pudo reactivarse")
    try:
        service.autenticar(token)
    except SesionNoVigente:
        pass
    else:
        raise AssertionError("Logout no invalidó el token")
    print("[OK] Logout irreversible incluso frente a guardar() tardío")

    # Sesión con actividad antigua; no afecta a las de otros usuarios.
    token_inactivo = secrets.token_urlsafe(32)
    base = ahora - timedelta(minutes=40)
    repo.guardar(Sesion(token_inactivo, usuario.id, base, base + timedelta(hours=8), base))
    try:
        service.autenticar(token_inactivo, ahora=ahora)
    except SesionNoVigente:
        pass
    else:
        raise AssertionError("No se invalidó sesión inactiva")
    assert repo.buscar(token_inactivo) is None
    print("[OK] Inactividad de 30 minutos")

    token_expirado = secrets.token_urlsafe(32)
    base = ahora - timedelta(hours=9)
    repo.guardar(Sesion(token_expirado, usuario.id, base, base + timedelta(hours=8), base))
    try:
        service.autenticar(token_expirado, ahora=ahora)
    except SesionNoVigente:
        pass
    else:
        raise AssertionError("No se invalidó sesión expirada")
    assert repo.buscar(token_expirado) is None
    print("[OK] Expiración absoluta de 8 horas")
    print("BD-04 INTEGRACIÓN: TODAS LAS COMPROBACIONES APROBADAS")


if __name__ == "__main__":
    main()
