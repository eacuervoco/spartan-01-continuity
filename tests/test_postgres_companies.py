"""RF02 PostgreSQL real: ejecución optativa SOLO tras aprobar destino y escrituras.

No aplica SQL ni crea esquemas. Requiere 001, 003 y 004 previamente aplicados
en continuity_rf01_test. Activar con CONTINUITY_RUN_COMPANY_PG_TESTS=1 y
CONTINUITY_TEST_DB_NAME=continuity_rf01_test; usar CONTINUITY_TEST_DB_HOST,
PORT, USER y PASSWORD. Sin activación, no lee credenciales ni conecta.

Conserva registros con UUID/correos únicos en la BD dedicada: el rol de empresa
solo tiene SELECT/INSERT. La limpieza administrativa se autoriza por separado.
"""
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timezone
from threading import Barrier
from uuid import uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.core.models import Credencial, Empresa, Usuario
from app.infrastructure.postgres_companies import PostgresCompanyRepository
from app.infrastructure.postgres_users import PostgresUserRepository

pytestmark = pytest.mark.skipif(
    os.getenv("CONTINUITY_RUN_COMPANY_PG_TESTS") != "1",
    reason="Pendiente aprobación de destino PostgreSQL, migración y escrituras",
)


@pytest.fixture
def conectar():
    if os.getenv("CONTINUITY_TEST_DB_NAME") != "continuity_rf01_test":
        pytest.fail("Destino de pruebas no autorizado", pytrace=False)
    if os.getenv("CONTINUITY_TEST_DB_USER") != "continuity_app":
        pytest.fail("Las pruebas requieren el rol continuity_app", pytrace=False)
    variables = ["HOST", "PORT", "PASSWORD"]
    if any(not os.getenv("CONTINUITY_TEST_DB_" + nombre) for nombre in variables):
        pytest.fail("Configuración de pruebas incompleta", pytrace=False)

    def abrir():
        try:
            return psycopg.connect(
                host=os.environ["CONTINUITY_TEST_DB_HOST"],
                port=int(os.environ["CONTINUITY_TEST_DB_PORT"]),
                dbname="continuity_rf01_test", user="continuity_app",
                password=os.environ["CONTINUITY_TEST_DB_PASSWORD"], connect_timeout=5,
            )
        except Exception:
            pytest.fail("No se pudo conectar al destino de pruebas", pytrace=False)

    with abrir() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user")
            assert cur.fetchone() == ("continuity_rf01_test", "continuity_app")
            cur.execute("SELECT to_regclass('public.empresas'), to_regclass('public.usuarios')")
            assert all(cur.fetchone()), "Falta preparar el esquema aprobado"
    return abrir


@pytest.fixture
def usuario(conectar):
    usuario = Usuario(uuid4(), "Prueba RF02", f"rf02-{uuid4().hex}@example.test",
                      datetime.now(timezone.utc))
    PostgresUserRepository(conectar).crear_cuenta(usuario, Credencial(usuario.id, "hash-de-prueba"))
    return usuario


def nueva_empresa(usuario_id, **cambios):
    datos = dict(id=uuid4(), usuario_id=usuario_id, nombre="Empresa RF02", ciudad="Bogotá",
                 creado_en=datetime.now(timezone.utc), nit="900123456-7", sector="Tecnología")
    datos.update(cambios)
    return Empresa(**datos)


def test_pg_persistencia_tras_reconexion(conectar, usuario):
    empresa = nueva_empresa(usuario.id)
    PostgresCompanyRepository(conectar).crear(empresa)
    assert PostgresCompanyRepository(conectar).buscar_por_usuario(usuario.id) == empresa


def test_pg_opcionales_y_aislamiento(conectar, usuario):
    repo = PostgresCompanyRepository(conectar)
    empresa = nueva_empresa(usuario.id, nit=None, sector=None)
    repo.crear(empresa)
    assert repo.buscar_por_usuario(usuario.id) == empresa
    assert repo.buscar_por_usuario(uuid4()) is None


def test_pg_fk_rechaza_usuario_inexistente(conectar):
    repo = PostgresCompanyRepository(conectar)
    usuario_id = uuid4()
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        repo.crear(nueva_empresa(usuario_id))
    assert repo.buscar_por_usuario(usuario_id) is None


def test_pg_unique_usuario_sin_sobrescritura(conectar, usuario):
    repo = PostgresCompanyRepository(conectar)
    original = nueva_empresa(usuario.id)
    repo.crear(original)
    with pytest.raises(ValueError, match="^Empresa duplicada$"):
        repo.crear(replace(original, id=uuid4(), nombre="Otra"))
    assert repo.buscar_por_usuario(usuario.id) == original


def test_pg_colision_concurrente(conectar, usuario):
    empresas = [nueva_empresa(usuario.id), nueva_empresa(usuario.id, nombre="Otra")]
    barrera = Barrier(2)

    def crear(empresa):
        barrera.wait(timeout=10)
        try:
            PostgresCompanyRepository(conectar).crear(empresa)
            return empresa
        except ValueError as exc:
            assert str(exc) == "Empresa duplicada"
            return None

    with ThreadPoolExecutor(max_workers=2) as executor:
        resultados = list(executor.map(crear, empresas))
    ganadoras = [r for r in resultados if r is not None]
    assert len(ganadoras) == 1
    assert PostgresCompanyRepository(conectar).buscar_por_usuario(usuario.id) == ganadoras[0]


def test_pg_fallo_de_insercion_no_deja_registro(conectar, usuario):
    repo = PostgresCompanyRepository(conectar)
    with pytest.raises((psycopg.Error, ValueError)):
        repo.crear(nueva_empresa(usuario.id, nit="invalido\x00"))
    assert repo.buscar_por_usuario(usuario.id) is None
    valida = nueva_empresa(usuario.id)
    repo.crear(valida)
    assert repo.buscar_por_usuario(usuario.id) == valida


def test_pg_permisos_minimos(conectar):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT has_table_privilege(current_user, 'public.empresas', 'SELECT'),
                                  has_table_privilege(current_user, 'public.empresas', 'INSERT'),
                                  has_table_privilege(current_user, 'public.empresas', 'UPDATE'),
                                  has_table_privilege(current_user, 'public.empresas', 'DELETE')""")
            assert cur.fetchone() == (True, True, False, False)


def test_pg_api_nueva_aplicacion_y_nueva_sesion(conectar, monkeypatch):
    import app.main as main

    monkeypatch.setenv("CONTINUITY_STORAGE", "postgres")
    monkeypatch.setenv("CONTINUITY_ENV", "production")
    monkeypatch.setattr(main, "nueva_conexion", conectar)
    correo, clave = f"rf02-api-{uuid4().hex}@example.com", "PruebaRF02!2026_Segura"
    with TestClient(main.create_app(), base_url="https://testserver") as client:
        assert client.post("/auth/register", json={"nombre": "Cliente RF02", "email": correo,
                           "password": clave, "confirmacion_password": clave}).status_code == 201
        assert client.post("/auth/login", json={"email": correo, "password": clave}).status_code == 200
        csrf = client.get("/auth/csrf").json()["csrf_token"]
        headers = {"X-CSRF-Token": csrf}
        datos = {"nombre": "Empresa persistida", "ciudad": "Bogotá"}
        respuesta = client.post("/auth/companies", headers=headers, json=datos)
        assert respuesta.status_code == 201
        original = respuesta.json()
        assert client.post("/auth/companies", headers=headers, json=datos).status_code == 409
        assert client.post("/auth/logout", headers=headers).status_code == 200
    with TestClient(main.create_app(), base_url="https://testserver") as client:
        assert client.post("/auth/login", json={"email": correo, "password": clave}).status_code == 200
        respuesta = client.get("/auth/companies/me")
        assert respuesta.status_code == 200 and respuesta.json() == original
