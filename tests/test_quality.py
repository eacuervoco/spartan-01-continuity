"""PBI-06: auditoría sin secretos y regresiones de seguridad HTTP."""
import logging

from fastapi.testclient import TestClient
from app.main import create_app

CLAVE = "ClaveSegura2026!"
CORREO = "auditoria@ejemplo.com"


def registrar(client, correo=CORREO):
    return client.post('/auth/register', json={
        'nombre': 'Auditoría', 'email': correo,
        'password': CLAVE, 'confirmacion_password': CLAVE})


def test_auditoria_cubre_registro_login_y_logout_sin_secretos(caplog):
    with caplog.at_level(logging.INFO, logger='continuity.audit'):
        with TestClient(create_app(), base_url='https://testserver') as client:
            assert registrar(client).status_code == 201
            assert registrar(client).status_code == 409
            assert client.post('/auth/login', json={'email': CORREO, 'password': 'incorrecta'}).status_code == 401
            assert client.post('/auth/login', json={'email': CORREO, 'password': CLAVE}).status_code == 200
            csrf = client.get('/auth/csrf').json()['csrf_token']
            cookie = client.cookies.get('continuity_session')
            assert client.post('/auth/logout', headers={'X-CSRF-Token': csrf}).status_code == 200
    mensajes = [r.getMessage() for r in caplog.records if r.name == 'continuity.audit']
    assert len(mensajes) == 5
    assert 'evento=registro resultado=exitoso codigo_http=201' in mensajes
    assert 'evento=registro resultado=fallido codigo_http=409' in mensajes
    assert 'evento=inicio_sesion resultado=fallido codigo_http=401' in mensajes
    assert 'evento=inicio_sesion resultado=exitoso codigo_http=200' in mensajes
    assert 'evento=cierre_sesion resultado=exitoso codigo_http=200' in mensajes
    texto = '\n'.join(mensajes)
    for secreto in (CLAVE, CORREO, csrf, cookie, 'incorrecta'):
        assert secreto not in texto


def test_auditoria_validacion_rechazada_sin_datos_sensibles(caplog):
    with caplog.at_level(logging.INFO, logger='continuity.audit'):
        with TestClient(create_app(), base_url='https://testserver') as client:
            r = client.post('/auth/register', json={'nombre': 'A', 'email': CORREO,
                'password': 'corta', 'confirmacion_password': 'corta'})
            assert r.status_code == 422
    assert 'evento=registro resultado=fallido codigo_http=422' in caplog.text
    assert CORREO not in caplog.text and 'corta' not in caplog.text


def test_logout_sin_csrf_es_rechazado_y_auditado(caplog):
    with caplog.at_level(logging.INFO, logger='continuity.audit'):
        with TestClient(create_app(), base_url='https://testserver') as client:
            assert registrar(client).status_code == 201
            assert client.post('/auth/login', json={'email': CORREO, 'password': CLAVE}).status_code == 200
            assert client.post('/auth/logout').status_code == 403
            assert client.get('/auth/session').status_code == 200
    assert 'evento=cierre_sesion resultado=fallido codigo_http=403' in caplog.text


def test_logout_no_permite_reutilizar_cookie_anterior():
    with TestClient(create_app(), base_url='https://testserver') as client:
        registrar(client)
        client.post('/auth/login', json={'email': CORREO, 'password': CLAVE})
        original = client.cookies.get('continuity_session')
        csrf = client.get('/auth/csrf').json()['csrf_token']
        assert client.post('/auth/logout', headers={'X-CSRF-Token': csrf}).status_code == 200
        client.cookies.set('continuity_session', original, path='/auth')
        assert client.get('/auth/session').status_code == 401
