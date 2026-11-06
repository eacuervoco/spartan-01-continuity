"""PBI-04: pruebas de ciclo de vida, cookies, origen y CSRF."""
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.core.session_service import SesionNoVigente

PASSWORD = "ContraseñaFuerte_2026!"


@pytest.fixture
def cliente():
    with TestClient(create_app(), base_url="https://testserver") as c:
        r = c.post('/auth/register', json={
            'nombre': 'Cliente', 'email': 'cliente@ejemplo.com',
            'password': PASSWORD, 'confirmacion_password': PASSWORD})
        assert r.status_code == 201
        yield c


def entrar(cliente):
    r = cliente.post('/auth/login', json={'email': 'cliente@ejemplo.com', 'password': PASSWORD})
    assert r.status_code == 200
    return cliente.cookies.get('continuity_session')


def test_ruta_protegida_sin_cookie(cliente):
    assert cliente.get('/auth/session').status_code == 401
    assert cliente.get('/auth/csrf').status_code == 401


def test_sesion_vigente(cliente):
    token = entrar(cliente)
    r = cliente.get('/auth/session')
    assert r.status_code == 200 and r.json()['estado_sesion'] == 'VIGENTE'
    assert cliente.app.state.sesiones.buscar(token) is not None


def test_actualizar_actividad_sin_extender_limite_absoluto(cliente):
    token = entrar(cliente)
    repo = cliente.app.state.sesiones
    previa = repo.buscar(token)
    cliente.get('/auth/session')
    nueva = repo.buscar(token)
    assert nueva.expira_en == previa.expira_en
    assert nueva.ultima_actividad_en >= previa.ultima_actividad_en


def test_inactividad_de_30_minutos(cliente):
    token = entrar(cliente)
    repo = cliente.app.state.sesiones
    sesion = repo.buscar(token)
    repo.guardar(replace(sesion, ultima_actividad_en=sesion.creado_en))
    with pytest.raises(SesionNoVigente):
        cliente.app.state.session_service.autenticar(token, sesion.creado_en + timedelta(minutes=30))
    assert repo.buscar(token) is None


def test_limite_absoluto_ocho_horas(cliente):
    token = entrar(cliente)
    repo = cliente.app.state.sesiones
    sesion = repo.buscar(token)
    repo.guardar(replace(sesion, ultima_actividad_en=sesion.expira_en))
    with pytest.raises(SesionNoVigente):
        cliente.app.state.session_service.autenticar(token, sesion.expira_en)
    assert repo.buscar(token) is None


def test_logout_requiere_csrf(cliente):
    token = entrar(cliente)
    assert cliente.post('/auth/logout').status_code == 403
    assert cliente.app.state.sesiones.buscar(token) is not None
    assert cliente.post('/auth/logout', headers={'x-csrf-token': 'incorrecto'}).status_code == 403


def test_logout_invalida_token_y_cookie(cliente):
    token = entrar(cliente)
    csrf = cliente.get('/auth/csrf').json()['csrf_token']
    r = cliente.post('/auth/logout', headers={'x-csrf-token': csrf})
    assert r.status_code == 200
    assert r.json() == {'mensaje': 'Sesión cerrada'}
    assert 'Max-Age=0' in r.headers['set-cookie']
    assert cliente.app.state.sesiones.buscar(token) is None
    assert cliente.get('/auth/session').status_code == 401
    cliente.cookies.set('continuity_session', token, path='/auth')
    assert cliente.get('/auth/session').status_code == 401


def test_csrf_es_especifico_para_cada_sesion(cliente):
    t1 = entrar(cliente)
    csrf1 = cliente.get('/auth/csrf').json()['csrf_token']
    t2 = entrar(cliente)
    csrf2 = cliente.get('/auth/csrf').json()['csrf_token']
    assert csrf1 != csrf2 and t1 != t2
    assert cliente.post('/auth/logout', headers={'x-csrf-token': csrf1}).status_code == 403
    assert cliente.post('/auth/logout', headers={'x-csrf-token': csrf2}).status_code == 200


@pytest.mark.parametrize('endpoint,body', [
    ('/auth/register', {'nombre': 'Otro', 'email': 'otro@ejemplo.com', 'password': PASSWORD, 'confirmacion_password': PASSWORD}),
    ('/auth/login', {'email': 'cliente@ejemplo.com', 'password': PASSWORD})
])
def test_origen_cruzado_rechazado(cliente, endpoint, body):
    r = cliente.post(endpoint, json=body, headers={'origin': 'https://externo.example'})
    assert r.status_code == 403
    r = cliente.post(endpoint, json=body, headers={'sec-fetch-site': 'cross-site'})
    assert r.status_code == 403


def test_logout_origen_cruzado_rechazado(cliente):
    entrar(cliente)
    csrf = cliente.get('/auth/csrf').json()['csrf_token']
    assert cliente.post('/auth/logout', headers={
        'x-csrf-token': csrf, 'origin': 'https://externo.example'}).status_code == 403


def test_sesion_ausente_no_se_reactiva(cliente):
    assert cliente.app.state.session_service._sesiones.buscar('desconocida') is None
    with pytest.raises(SesionNoVigente):
        cliente.app.state.session_service.autenticar('desconocida', datetime.now(timezone.utc))
