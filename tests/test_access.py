"""PBI-05: identidad, destinos y acceso cerrado por defecto."""
from uuid import uuid4
from fastapi.testclient import TestClient
import pytest
from app.main import create_app
from app.core.access_service import AccessService, DestinoAcceso, UsuarioNoDisponible

PASSWORD = "ContraseñaFuerte_2026!"


@pytest.fixture
def cliente():
    with TestClient(create_app(), base_url="https://testserver") as c:
        assert c.post('/auth/register', json={
            'nombre':'Cliente', 'email':'CLIENTE@ejemplo.com',
            'password':PASSWORD, 'confirmacion_password':PASSWORD}).status_code == 201
        yield c


def login(cliente):
    assert cliente.post('/auth/login', json={
        'email':'cliente@ejemplo.com', 'password':PASSWORD}).status_code == 200


def test_me_requiere_sesion(cliente):
    assert cliente.get('/auth/me').status_code == 401


def test_me_muestra_contexto_minimo_sin_secretos(cliente):
    login(cliente)
    r = cliente.get('/auth/me')
    assert r.status_code == 200
    assert r.json()['email'] == 'cliente@ejemplo.com'
    assert r.json()['rol'] == 'CLIENTE'
    assert r.json()['estado'] == 'ACTIVA'
    assert r.json()['destino'] == 'INCORPORACION_EMPRESARIAL'
    assert set(r.json()) == {'id', 'nombre', 'email', 'estado', 'rol', 'destino'}
    assert PASSWORD not in r.text and 'hash' not in r.text and 'token' not in r.text


def test_me_despues_de_logout_es_401(cliente):
    login(cliente)
    csrf = cliente.get('/auth/csrf').json()['csrf_token']
    assert cliente.post('/auth/logout', headers={'X-CSRF-Token': csrf}).status_code == 200
    assert cliente.get('/auth/me').status_code == 401


def test_me_usuario_eliminado_rechazado(cliente):
    login(cliente)
    id_usuario = cliente.get('/auth/me').json()['id']
    repo = cliente.app.state.usuarios
    repo._usuarios.pop(__import__('uuid').UUID(id_usuario))
    assert cliente.get('/auth/me').status_code == 401


def test_servicio_permite_panel_solo_con_autorizacion_explicita(cliente):
    login(cliente)
    from uuid import UUID
    uid = UUID(cliente.get('/auth/me').json()['id'])
    class Autorizado:
        def tiene_asociacion_autorizada(self, usuario_id):
            return usuario_id == uid
    resultado = AccessService(cliente.app.state.usuarios, Autorizado()).consultar(uid)
    assert resultado.destino is DestinoAcceso.PANEL


@pytest.mark.parametrize('respuesta', [None, 0, 'True', False])
def test_autorizacion_ambigua_no_da_panel(cliente, respuesta):
    login(cliente)
    from uuid import UUID
    uid = UUID(cliente.get('/auth/me').json()['id'])
    class Ambigua:
        def tiene_asociacion_autorizada(self, usuario_id):
            return respuesta
    assert AccessService(cliente.app.state.usuarios, Ambigua()).consultar(uid).destino is DestinoAcceso.INCORPORACION_EMPRESARIAL


def test_error_membership_falla_cerrado(cliente):
    login(cliente)
    from uuid import UUID
    uid = UUID(cliente.get('/auth/me').json()['id'])
    class Rota:
        def tiene_asociacion_autorizada(self, usuario_id):
            raise RuntimeError('BD no disponible')
    assert AccessService(cliente.app.state.usuarios, Rota()).consultar(uid).destino is DestinoAcceso.INCORPORACION_EMPRESARIAL


def test_usuario_ausente_servicio():
    app = create_app()
    with pytest.raises(UsuarioNoDisponible):
        app.state.access_service.consultar(uuid4())
