"""Pruebas de servicio y contrato HTTP del PBI-02."""
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.core.registration import RegistroService, CorreoDuplicado, RegistroInvalido
from app.infrastructure.memory import MemoryUserRepository
from app.infrastructure.security import Argon2PasswordHasher

PASSWORD = "ContraseñaFuerte_2026!"

@pytest.fixture
def cliente():
    with TestClient(create_app()) as client:
        yield client


def datos(**cambios):
    body = {"nombre": "  Empresa Cliente  ", "email": "  CLIENTE@Ejemplo.COM  ",
            "password": PASSWORD, "confirmacion_password": PASSWORD}
    body.update(cambios)
    return body


def test_registro_valido_sin_inicio_de_sesion(cliente):
    r = cliente.post("/auth/register", json=datos())
    assert r.status_code == 201
    assert r.json()["email"] == "cliente@ejemplo.com"
    assert r.json()["nombre"] == "Empresa Cliente"
    assert r.json()["estado"] == "ACTIVA"
    assert r.json()["rol"] == "CLIENTE"
    assert "password" not in r.json() and "password_hash" not in r.json()
    assert "set-cookie" not in r.headers
    usuario = cliente.app.state.usuarios.buscar_por_correo("cliente@ejemplo.com")
    hash_almacenado = cliente.app.state.usuarios.buscar_credencial(usuario.id).password_hash
    assert hash_almacenado != PASSWORD
    assert hash_almacenado.startswith("$argon2id$")
    assert Argon2PasswordHasher().verificar(PASSWORD, hash_almacenado)
    assert not Argon2PasswordHasher().verificar("incorrecta", hash_almacenado)


def test_correo_duplicado_case_insensitive(cliente):
    assert cliente.post("/auth/register", json=datos()).status_code == 201
    assert cliente.post("/auth/register", json=datos(email="cliente@EJEMPLO.com")).status_code == 409


@pytest.mark.parametrize("changes", [
    {"password": "corta", "confirmacion_password": "corta"},
    {"confirmacion_password": "OtraContraseñaLarga123"},
    {"email": "sin-arroba"},
    {"nombre": "   "},
])
def test_datos_invalidos(cliente, changes):
    assert cliente.post("/auth/register", json=datos(**changes)).status_code == 422
    assert cliente.app.state.usuarios.buscar_por_correo("cliente@ejemplo.com") is None


def test_campos_extra_rechazados(cliente):
    assert cliente.post("/auth/register", json=datos(rol="ADMIN")).status_code == 422


def test_fallo_del_hash_no_crea_usuario():
    class HashFalla:
        def generar_hash(self, password):
            raise RuntimeError("fallo de hashing")
        def verificar(self, password, password_hash):
            return False
    repo = MemoryUserRepository()
    servicio = RegistroService(repo, HashFalla())
    with pytest.raises(RuntimeError):
        servicio.registrar("Cliente", "cliente@ejemplo.com", PASSWORD, PASSWORD)
    assert repo.buscar_por_correo("cliente@ejemplo.com") is None


def test_fallo_repositorio_no_expone_excepcion(cliente):
    class RepoFalla(MemoryUserRepository):
        def crear_cuenta(self, usuario, credencial):
            raise RuntimeError("detalle interno sensible")
    repo = RepoFalla()
    cliente.app.state.registro_service = RegistroService(repo, Argon2PasswordHasher())
    r = cliente.post("/auth/register", json=datos())
    assert r.status_code == 503
    assert "detalle interno sensible" not in r.text


def test_colision_en_guardado_transformada_a_conflicto(cliente):
    class RepoColision(MemoryUserRepository):
        def crear_cuenta(self, usuario, credencial):
            raise ValueError("Cuenta duplicada")
    cliente.app.state.registro_service = RegistroService(RepoColision(), Argon2PasswordHasher())
    assert cliente.post("/auth/register", json=datos()).status_code == 409
