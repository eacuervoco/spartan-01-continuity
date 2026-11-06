"""Pruebas manuales BD-03: SOLO base dedicada continuity_rf01_test.

Ejecutar desde la raiz del repositorio: python -m tests... (o ejecutar este script).
No modifica continuity_db ni crea/elimina esquemas/tablas.
"""
from __future__ import annotations

import getpass
import os
from datetime import datetime, timezone
from uuid import uuid4

import psycopg

from app.core.models import Credencial, Usuario
from app.core.registration import CorreoDuplicado, RegistroService
from app.infrastructure.postgres_users import PostgresUserRepository
from app.infrastructure.security import Argon2PasswordHasher


def main() -> None:
    database = os.getenv("CONTINUITY_TEST_DB_NAME", "continuity_rf01_test")
    if database != "continuity_rf01_test":
        raise SystemExit("SEGURIDAD: usar exclusivamente continuity_rf01_test")

    password = os.getenv("CONTINUITY_TEST_DB_PASSWORD") or getpass.getpass("Contraseña continuity_app (BD de pruebas): ")
    settings = dict(
        host="127.0.0.1", port=15432, dbname=database,
        user="continuity_app", password=password, connect_timeout=5,
    )

    def connect():
        return psycopg.connect(**settings)

    # Comprobación explícita del destino ANTES de escribir cualquier registro.
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user")
            assert cur.fetchone() == ("continuity_rf01_test", "continuity_app")
            cur.execute("SELECT to_regclass('public.usuarios'), to_regclass('public.credenciales')")
            assert all(cur.fetchone()), "Falta aplicar migración BD-02 en la BD de pruebas"
    print("[OK] Destino aislado y esquema disponibles")

    repo = PostgresUserRepository(connect)
    hasher = Argon2PasswordHasher()
    registro = RegistroService(repo, hasher)
    email = f"bd03-{uuid4().hex}@example.test"
    clave = "PruebaRF01!2026_Segura"

    usuario = registro.registrar("Prueba BD03", email.upper(), clave, clave)
    encontrado = repo.buscar_por_correo(email)
    assert encontrado == usuario
    assert repo.buscar_por_id(usuario.id) == usuario
    credencial = repo.buscar_credencial(usuario.id)
    assert credencial is not None
    assert credencial.password_hash.startswith("$argon2id$")
    assert credencial.password_hash != clave
    assert hasher.verificar(clave, credencial.password_hash)
    print("[OK] Registro y credencial persistidos y recuperados (reconexión incluida)")

    try:
        registro.registrar("Duplicado", email, clave, clave)
    except CorreoDuplicado:
        print("[OK] Duplicado controlado por servicio")
    else:
        raise AssertionError("No se rechazó correo duplicado")

    # Verifica la restricción UNIQUE directamente (sin comprobación previa).
    segundo = Usuario(id=uuid4(), nombre="Prueba colisión", email_normalizado=email,
                      creado_en=datetime.now(timezone.utc))
    try:
        repo.crear_cuenta(segundo, Credencial(segundo.id, hasher.generar_hash(clave)))
    except ValueError as exc:
        assert str(exc) == "Cuenta duplicada"
        assert repo.buscar_por_id(segundo.id) is None
        print("[OK] UNIQUE rechaza colisión; no hay usuario huérfano")
    else:
        raise AssertionError("UNIQUE no rechazó correo duplicado")

    # Inyección de valor inválido para provocar error en segunda inserción.
    # Credencial admite la cadena, pero PostgreSQL rechaza el byte NUL.
    rollback_user = Usuario(id=uuid4(), nombre="Prueba rollback",
                            email_normalizado=f"rollback-{uuid4().hex}@example.test",
                            creado_en=datetime.now(timezone.utc))
    try:
        repo.crear_cuenta(rollback_user, Credencial(rollback_user.id, "hash\x00invalido"))
    except (psycopg.Error, ValueError):
        assert repo.buscar_por_id(rollback_user.id) is None
        print("[OK] Falla segunda inserción y se revierte la primera")
    else:
        raise AssertionError("La inserción inválida no falló como se esperaba")

    print("BD-03 INTEGRACIÓN: TODAS LAS COMPROBACIONES APROBADAS")


if __name__ == "__main__":
    main()
