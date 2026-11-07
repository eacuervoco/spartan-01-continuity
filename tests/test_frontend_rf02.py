"""Contrato HTML, integración HTTP en memoria y ejecución JS sin navegador."""
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

ROOT = Path(__file__).resolve().parents[1]


class Elements(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.elements = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


def test_empresa_semantica_oculta_y_campos_accesibles():
    html = (ROOT / "app/templates/access.html").read_text(encoding="utf-8")
    elements = Elements(html).elements
    ids = {attrs["id"]: attrs for _, attrs in elements if "id" in attrs}
    assert sum(tag == "h1" for tag, _ in elements) == 1
    assert 'lang="es"' in html and 'charset="UTF-8"' in html
    assert "hidden" in ids["company-section"]
    assert ids["show-company"]["aria-controls"] == "company-section"
    assert ids["show-company"]["aria-expanded"] == "false"
    labels = {attrs["for"] for tag, attrs in elements if tag == "label"}
    for field, length, required in [("name", 150, True), ("city", 100, True),
                                    ("nit", 20, False), ("sector", 100, False)]:
        key = "company-" + field
        assert key in labels
        assert ids[key]["maxlength"] == str(length)
        assert ("required" in ids[key]) == required
    assert sum(tag == "dt" for tag, _ in elements) == 4
    assert sum(tag == "dd" for tag, _ in elements) == 4
    assert "hidden" in ids["company-form"] and "hidden" in ids["company-details"]
    assert ids["company-feedback"]["aria-live"] == "polite"
    assert '<script>' not in html and '<style' not in html and 'onclick=' not in html


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("CONTINUITY_STORAGE", "memory")
    monkeypatch.setenv("CONTINUITY_ENV", "production")
    with TestClient(create_app(), base_url="https://testserver") as c:
        yield c


def test_access_y_recursos_empresa_se_sirven(client):
    assert 'id="company-section"' in client.get("/access").text
    for path in ["/static/css/company.css", "/static/css/base.css", "/static/css/login.css",
                 "/static/js/access.js", "/static/js/common.js"]:
        assert client.get(path).status_code == 200


@pytest.mark.parametrize("opcionales", [{}, {"nit": "900123456-7", "sector": "Tecnología"}])
def test_flujo_http_access_empresa_y_nueva_sesion(client, opcionales):
    """HTTP real, sin ejecutar JS ni afirmar persistencia PostgreSQL."""
    credentials = {"email": "frontend@example.com", "password": "ClaveRF02!2026_Segura"}
    assert client.post("/auth/register", json={"nombre": "Cliente", **credentials,
                       "confirmacion_password": credentials["password"]}).status_code == 201
    assert client.post("/auth/login", json=credentials).status_code == 200
    assert client.get("/access").status_code == 200
    assert client.get("/auth/companies/me").status_code == 404
    payload = {"nombre": " Empresa Bogotá ", "ciudad": " Bogotá ", **opcionales}
    assert client.post("/auth/companies", json=payload).status_code == 403
    token = client.get("/auth/csrf").json()["csrf_token"]
    headers = {"X-CSRF-Token": token}
    result = client.post("/auth/companies", headers=headers, json=payload)
    assert result.status_code == 201
    company = result.json()
    assert company["nombre"] == "Empresa Bogotá"
    assert company["nit"] == opcionales.get("nit")
    assert client.post("/auth/companies", headers=headers, json=payload).status_code == 409
    assert client.post("/auth/logout", headers=headers).status_code == 200
    assert client.get("/auth/companies/me").status_code == 401
    assert client.post("/auth/login", json=credentials).status_code == 200
    assert client.get("/auth/companies/me").json() == company


def test_javascript_rf02_con_dom_simulado():
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node no disponible para ejecutar JavaScript; no requiere instalar paquetes")
    result = subprocess.run([node, "tests/frontend_rf02.test.cjs"], cwd=ROOT,
                            text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
