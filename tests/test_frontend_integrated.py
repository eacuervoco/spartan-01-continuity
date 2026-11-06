"""Pruebas de integración para PBI-F02, F03 y F04."""
import re
from fastapi.testclient import TestClient
from app.main import create_app


def client():
    return TestClient(create_app(), base_url="https://testserver")


def test_vistas_y_metadatos():
    with client() as c:
        for path, form_id in (("/login", "login-form"), ("/register", "register-form"), ("/access", None)):
            r = c.get(path)
            assert r.status_code == 200
            assert 'lang="es"' in r.text
            assert 'charset="UTF-8"' in r.text
            assert len(re.findall(r"<h1(?:\s|>)", r.text, re.I)) == 1
            assert '<style' not in r.text and '<script>' not in r.text
            assert 'noindex' in r.text
            if form_id:
                assert f'id="{form_id}"' in r.text


def test_recursos_estaticos_por_separado():
    with client() as c:
        for resource in ('common.js', 'login.js', 'register.js', 'access.js'):
            r = c.get('/static/js/' + resource)
            assert r.status_code == 200
        for resource in ('base.css', 'login.css'):
            assert c.get('/static/css/' + resource).status_code == 200


def test_registro_login_contexto_y_logout():
    with client() as c:
        payload = {"nombre": "Empresa de Prueba", "email": "integrada@example.com", "password": "ClaveMuySegura2026!", "confirmacion_password": "ClaveMuySegura2026!"}
        registered = c.post('/auth/register', json=payload)
        assert registered.status_code == 201
        login = c.post('/auth/login', json={"email": payload['email'], "password": payload['password']})
        assert login.status_code == 200
        assert 'httponly' in login.headers['set-cookie'].lower()
        assert 'samesite=lax' in login.headers['set-cookie'].lower()
        me = c.get('/auth/me')
        assert me.status_code == 200
        assert me.json()['destino'] == 'INCORPORACION_EMPRESARIAL'
        no_csrf = c.post('/auth/logout')
        assert no_csrf.status_code == 403
        token = c.get('/auth/csrf').json()['csrf_token']
        out = c.post('/auth/logout', headers={'X-CSRF-Token': token})
        assert out.status_code == 200
        assert c.get('/auth/me').status_code == 401


def test_sin_autenticacion_no_hay_contexto():
    with client() as c:
        assert c.get('/auth/me').status_code == 401
        assert c.get('/auth/csrf').status_code == 401


def test_login_mensaje_generico():
    with client() as c:
        r = c.post('/auth/login', json={'email': 'missing@example.com', 'password': 'x'})
        assert r.status_code == 401
        assert r.json()['detail'] == 'Credenciales inválidas'


def test_registro_rechaza_contrasenas_distintas():
    with client() as c:
        r = c.post('/auth/register', json={'nombre':'Ejemplo','email':'other@example.com','password':'ClaveMuySegura2026!','confirmacion_password':'otra-contraseña'})
        assert r.status_code == 422


def test_no_se_exponen_secretos_en_me():
    with client() as c:
        payload={'nombre':'Ejemplo','email':'secret@example.com','password':'ClaveMuySegura2026!','confirmacion_password':'ClaveMuySegura2026!'}
        c.post('/auth/register', json=payload)
        c.post('/auth/login', json={'email': payload['email'], 'password':payload['password']})
        body = c.get('/auth/me').text.lower()
        assert 'password' not in body and 'token' not in body and 'hash' not in body


def test_csrf_incorrecto_no_cierra_sesion():
    with client() as c:
        p={'nombre':'Otro','email':'csrf@example.com','password':'ClaveMuySegura2026!','confirmacion_password':'ClaveMuySegura2026!'}
        c.post('/auth/register', json=p)
        c.post('/auth/login', json={'email':p['email'],'password':p['password']})
        assert c.post('/auth/logout', headers={'X-CSRF-Token':'invalido'}).status_code == 403
        assert c.get('/auth/me').status_code == 200
