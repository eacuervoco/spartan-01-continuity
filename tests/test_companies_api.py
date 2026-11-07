"""API RF02 con sesiones y CSRF reales de RF01, almacenamiento en memoria."""
from dataclasses import replace
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.company_service import EmpresaService
from app.main import create_app

URL = "/auth/companies"
PASSWORD = "ClaveRF02!2026_Segura"


def entrar(client, correo="empresa@example.com"):
    assert client.post("/auth/register", json={
        "nombre": "Cliente", "email": correo,
        "password": PASSWORD, "confirmacion_password": PASSWORD,
    }).status_code == 201
    assert client.post("/auth/login", json={"email": correo, "password": PASSWORD}).status_code == 200
    return {"X-CSRF-Token": client.get("/auth/csrf").json()["csrf_token"]}


@pytest.fixture
def cliente(monkeypatch):
    monkeypatch.setenv("CONTINUITY_STORAGE", "memory")
    monkeypatch.setenv("CONTINUITY_ENV", "production")
    with TestClient(create_app(), base_url="https://testserver") as client:
        yield client


@pytest.fixture
def autorizado(cliente):
    return cliente, entrar(cliente)


def test_registro_y_consulta_publica_con_normalizacion(autorizado):
    client, headers = autorizado
    respuesta = client.post(URL, headers=headers, json={
        "nombre": " TecniRed  Sabana ", "ciudad": " Bogotá ",
        "nit": " 900123456-7 ", "sector": " Tecnología ",
    })
    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert set(datos) == {"id", "nombre", "ciudad", "nit", "sector", "creado_en"}
    assert UUID(datos["id"]).version == 4
    assert datos["creado_en"].endswith("Z")
    assert datos["nombre"] == "TecniRed  Sabana" and datos["ciudad"] == "Bogotá"
    assert datos["nit"] == "900123456-7" and datos["sector"] == "Tecnología"
    consulta = client.get(URL + "/me")
    assert consulta.status_code == 200 and consulta.json() == datos
    usuario = client.app.state.usuarios.buscar_por_correo("empresa@example.com")
    assert client.app.state.empresas.buscar_por_usuario(usuario.id).id == UUID(datos["id"])


def test_limites_normalizados_y_opcionales_omitidos(autorizado):
    client, headers = autorizado
    respuesta = client.post(URL, headers=headers,
                           json={"nombre": " " + "á" * 150 + " ", "ciudad": "ñ" * 100})
    assert respuesta.status_code == 201
    assert len(respuesta.json()["nombre"]) == 150
    assert respuesta.json()["nit"] is None and respuesta.json()["sector"] is None


@pytest.mark.parametrize("opcionales", [{"nit": None, "sector": None}, {"nit": " \t", "sector": "\n"}])
def test_opcionales_nulos_o_vacios(autorizado, opcionales):
    client, headers = autorizado
    respuesta = client.post(URL, headers=headers, json={"nombre": "Empresa", "ciudad": "Cali", **opcionales})
    assert respuesta.status_code == 201
    assert respuesta.json()["nit"] is None and respuesta.json()["sector"] is None


@pytest.mark.parametrize("cambio", [
    {"nombre": " \t"}, {"ciudad": ""}, {"nombre": "a" * 151},
    {"ciudad": "a" * 101}, {"nit": "1" * 21}, {"sector": "a" * 101},
    {"nombre": None}, {"nit": 123}, {"usuario_id": str(uuid4())},
])
def test_entrada_invalida_no_guarda(autorizado, cambio):
    client, headers = autorizado
    respuesta = client.post(URL, headers=headers, json={"nombre": "Empresa", "ciudad": "Cali", **cambio})
    assert respuesta.status_code == 422
    assert client.get(URL + "/me").status_code == 404


@pytest.mark.parametrize("metodo,ruta", [("post", URL), ("get", URL + "/me")])
def test_sin_sesion_es_401(cliente, metodo, ruta):
    kwargs = {"json": {"nombre": "Empresa", "ciudad": "Cali"}} if metodo == "post" else {}
    assert getattr(cliente, metodo)(ruta, **kwargs).status_code == 401


@pytest.mark.parametrize("estado", ["inactiva", "expirada", "revocada"])
def test_sesion_no_vigente_rechazada(autorizado, estado):
    client, headers = autorizado
    token = client.cookies.get("continuity_session")
    repo = client.app.state.sesiones
    if estado == "revocada":
        repo.invalidar(token)
    else:
        sesion = repo.buscar(token)
        fecha = sesion.creado_en - timedelta(hours=9 if estado == "expirada" else 1)
        repo.guardar(replace(sesion, creado_en=fecha, ultima_actividad_en=fecha,
                             expira_en=fecha + timedelta(hours=8)))
    assert client.post(URL, headers=headers, json={"nombre": "Empresa", "ciudad": "Cali"}).status_code == 401
    assert client.get(URL + "/me").status_code == 401


@pytest.mark.parametrize("headers", [{}, {"X-CSRF-Token": "incorrecto"}])
def test_csrf_requerido(autorizado, headers):
    client, _ = autorizado
    assert client.post(URL, headers=headers, json={"nombre": "Empresa", "ciudad": "Cali"}).status_code == 403
    assert client.get(URL + "/me").status_code == 404


@pytest.mark.parametrize("origen", [{"Origin": "https://otro.example"}, {"Sec-Fetch-Site": "cross-site"}])
def test_origen_rechazado(autorizado, origen):
    client, headers = autorizado
    assert client.post(URL, headers={**headers, **origen},
                       json={"nombre": "Empresa", "ciudad": "Cali"}).status_code == 403
    assert client.get(URL + "/me").status_code == 404


def test_duplicado_409_conserva_original(autorizado):
    client, headers = autorizado
    original = client.post(URL, headers=headers, json={"nombre": "Original", "ciudad": "Cali"})
    assert original.status_code == 201
    assert client.post(URL, headers=headers, json={"nombre": "Otra", "ciudad": "Cali"}).status_code == 409
    assert client.get(URL + "/me").json() == original.json()


def test_aislamiento_y_csrf_ligado_a_sesion(autorizado):
    client, headers_a = autorizado
    datos = {"nombre": "Empresa A", "ciudad": "Cali", "nit": "900123456-7"}
    primera = client.post(URL, headers=headers_a, json=datos).json()
    headers_b = entrar(client, "otra@example.com")
    assert client.get(URL + "/me").status_code == 404
    assert client.post(URL, headers=headers_a, json=datos).status_code == 403
    segunda = client.post(URL, headers=headers_b, json={**datos, "nombre": "Empresa B"})
    assert segunda.status_code == 201 and segunda.json()["id"] != primera["id"]
    assert client.get(URL + "/me").json() == segunda.json()


@pytest.mark.parametrize("operacion", ["crear", "buscar_por_usuario", "sesion", "respuesta"])
def test_fallos_internos_son_500_sin_detalles(autorizado, monkeypatch, operacion):
    client, headers = autorizado

    def fallar(*args, **kwargs):
        raise RuntimeError("detalle-interno-no-publico")

    if operacion == "sesion":
        monkeypatch.setattr(client.app.state.session_service, "autenticar", fallar)
    elif operacion == "respuesta":
        monkeypatch.setattr(client.app.state.empresa_service, "consultar", lambda uid: object())
    else:
        monkeypatch.setattr(client.app.state.empresas, operacion, fallar)
    respuesta = (client.post(URL, headers=headers, json={"nombre": "Empresa", "ciudad": "Cali"})
                 if operacion == "crear" else client.get(URL + "/me"))
    assert respuesta.status_code == 500
    assert respuesta.json() == {"detail": "Operación de empresa temporalmente no disponible"}
    assert "detalle-interno" not in respuesta.text


def test_colision_de_guardado_devuelve_409(autorizado, monkeypatch):
    client, headers = autorizado

    def colision(empresa):
        raise ValueError("Empresa duplicada")

    monkeypatch.setattr(client.app.state.empresas, "crear", colision)
    assert client.post(URL, headers=headers, json={"nombre": "Empresa", "ciudad": "Cali"}).status_code == 409


def test_modo_postgres_compone_sin_conectar(monkeypatch):
    import app.main as main
    from app.infrastructure.postgres_companies import PostgresCompanyRepository

    def no_conectar():
        pytest.fail("La composición no debe abrir conexiones")

    monkeypatch.setenv("CONTINUITY_STORAGE", "postgres")
    monkeypatch.setattr(main, "nueva_conexion", no_conectar)
    app = main.create_app()
    assert isinstance(app.state.empresas, PostgresCompanyRepository)
    assert isinstance(app.state.empresa_service, EmpresaService)
