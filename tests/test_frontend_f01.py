"""Verificaciones de integración y contrato semántico de PBI-F01."""
from html.parser import HTMLParser
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import create_app

ROOT = Path(__file__).resolve().parents[1] / "app"

class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.attrs = []
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attrs.append((tag, dict(attrs)))


def test_pagina_login_se_sirve_con_utf8_y_meta_basicas():
    response = TestClient(create_app()).get("/login")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert '<meta charset="UTF-8">' in response.text
    assert 'lang="es"' in response.text
    assert 'name="viewport"' in response.text
    assert 'name="robots" content="noindex, nofollow"' in response.text


def test_semantica_un_solo_h1_y_campos_etiquetados():
    parsed = Elements()
    parsed.feed((ROOT / "templates/login.html").read_text(encoding="utf8"))
    assert parsed.tags.count("h1") == 1
    for tag in ("header", "main", "section", "aside", "footer", "form"):
        assert tag in parsed.tags
    ids = {d["id"] for _, d in parsed.attrs if "id" in d}
    labels = {d["for"] for t, d in parsed.attrs if t == "label"}
    assert {"email", "password"} <= ids
    assert {"email", "password"} <= labels


def test_codigo_y_estilos_externos():
    doc = (ROOT / "templates/login.html").read_text(encoding="utf8")
    assert "<style" not in doc and "<script>" not in doc
    assert "style=" not in doc and "onclick=" not in doc
    with TestClient(create_app()) as client:
        for path in ("/static/css/base.css", "/static/css/login.css", "/static/js/login.js"):
            assert client.get(path).status_code == 200


def test_api_anterior_continua_disponible():
    with TestClient(create_app()) as client:
        assert client.get("/openapi.json").status_code == 200
        assert client.get("/auth/me").status_code == 401
        assert client.get("/").headers["content-type"].startswith("text/html")
