"""Pruebas PBI-03: endpoint, servicio, seguridad de sesión y límites."""
import re
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
import pytest
from app.main import create_app
from app.core.login import CredencialesInvalidas
from app.core.models import EstadoSesion

PASSWORD = "ContraseñaFuerte_2026!"

@pytest.fixture
def cliente():
    with TestClient(create_app()) as c:
        assert c.post("/auth/register", json={
            "nombre": "Cliente", "email": "cliente@ejemplo.com", "password": PASSWORD,
            "confirmacion_password": PASSWORD}).status_code == 201
        yield c


def test_login_correcto_crea_sesion_y_cookie(cliente):
    r = cliente.post("/auth/login", json={"email": "CLIENTE@EJEMPLO.COM", "password": PASSWORD})
    assert r.status_code == 200
    assert r.json() == {"mensaje": "Autenticación exitosa"}
    cookie = r.headers["set-cookie"]
    assert "HttpOnly" in cookie and "Secure" in cookie and "SameSite=lax" in cookie
    assert "Path=/auth" in cookie
    token = cliente.cookies.get("continuity_session")
    assert token and len(token) >= 40
    assert PASSWORD not in r.text and token not in r.text
    sesion = cliente.app.state.sesiones.buscar(token)
    assert sesion is not None
    assert sesion.estado_en(datetime.now(timezone.utc)) is EstadoSesion.VIGENTE
    assert timedelta(hours=7, minutes=59) < sesion.expira_en - sesion.creado_en <= timedelta(hours=8)


@pytest.mark.parametrize("email,password", [
    ("ausente@ejemplo.com", PASSWORD),
    ("cliente@ejemplo.com", "contraseña-incorrecta"),
])
def test_login_invalido_mensaje_generico_y_sin_cookie(cliente, email, password):
    r = cliente.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 401 and r.json()["detail"] == "Credenciales inválidas"
    assert "set-cookie" not in r.headers
    assert cliente.app.state.sesiones._sesiones == {}


def test_limitador_ip_y_correo(cliente):
    for _ in range(5):
        assert cliente.post("/auth/login", json={"email": "cliente@ejemplo.com", "password": "errada"}).status_code == 401
    r = cliente.post("/auth/login", json={"email": "cliente@ejemplo.com", "password": PASSWORD})
    assert r.status_code == 429 and r.headers["retry-after"] == "900"
    # Otro correo tampoco evade el límite por IP.
    assert cliente.post("/auth/login", json={"email": "otro@ejemplo.com", "password": "errada"}).status_code == 429


def test_sesiones_distintas_por_login(cliente):
    body = {"email": "cliente@ejemplo.com", "password": PASSWORD}
    assert cliente.post("/auth/login", json=body).status_code == 200
    token1 = cliente.cookies.get("continuity_session")
    assert cliente.post("/auth/login", json=body).status_code == 200
    token2 = cliente.cookies.get("continuity_session")
    assert token1 != token2


def test_password_no_se_expone_en_validacion(cliente):
    r = cliente.post("/auth/login", json={"email": "cliente@ejemplo.com", "password": PASSWORD, "rol": "ADMIN"})
    assert r.status_code == 422 and "set-cookie" not in r.headers


def test_no_se_guarda_sesion_si_falla_validacion(cliente):
    class RepoFalla:
        def guardar(self, sesion):
            raise RuntimeError("detalle interno")
    cliente.app.state.login_service._sesiones = RepoFalla()
    r = cliente.post("/auth/login", json={"email": "cliente@ejemplo.com", "password": PASSWORD})
    assert r.status_code == 503 and "detalle interno" not in r.text and "set-cookie" not in r.headers


def test_credencial_inexistente_no_autentica(cliente):
    repo = cliente.app.state.usuarios
    usuario = repo.buscar_por_correo("cliente@ejemplo.com")
    repo._credenciales.pop(usuario.id)
    r = cliente.post("/auth/login", json={"email": "cliente@ejemplo.com", "password": PASSWORD})
    assert r.status_code == 401
