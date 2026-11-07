"""RF02 Bloque 1: dominio y servicio, sin HTTP ni PostgreSQL."""
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest

from app.core.company_service import EmpresaDuplicada, EmpresaInvalida, EmpresaService
from app.core.models import Empresa
from app.core.repositories import CompanyRepository


class CompanyRepositoryFake:
    """Doble local; no representa persistencia real ni valida concurrencia."""
    def __init__(self):
        self.empresas = {}

    def buscar_por_usuario(self, usuario_id):
        return self.empresas.get(usuario_id)

    def crear(self, empresa):
        if empresa.usuario_id in self.empresas:
            raise ValueError("Empresa duplicada")
        self.empresas[empresa.usuario_id] = empresa


@pytest.fixture
def repo():
    return CompanyRepositoryFake()


def test_registro_genera_uuid_fecha_utc_y_asocia_usuario(repo):
    usuario_id = uuid4()
    antes = datetime.now(timezone.utc)
    empresa = EmpresaService(repo).registrar(usuario_id, "TecniRed", "Bogotá")
    assert isinstance(repo, CompanyRepository)
    assert isinstance(empresa.id, UUID) and empresa.id.version == 4
    assert empresa.usuario_id == usuario_id
    assert empresa.nombre == "TecniRed" and empresa.ciudad == "Bogotá"
    assert empresa.creado_en.tzinfo is timezone.utc
    assert antes <= empresa.creado_en <= datetime.now(timezone.utc)
    assert repo.buscar_por_usuario(usuario_id) is empresa
    assert empresa.nit is None and empresa.sector is None


def test_normaliza_extremos_y_conserva_espacios_internos(repo):
    empresa = EmpresaService(repo).registrar(
        uuid4(), " \tTecniRed  Sabana\n", "  Bogotá  D.C. ",
        nit=" 900123456-7 ", sector=" Servicios  tecnológicos ",
    )
    assert empresa.nombre == "TecniRed  Sabana"
    assert empresa.ciudad == "Bogotá  D.C."
    assert empresa.nit == "900123456-7"
    assert empresa.sector == "Servicios  tecnológicos"


def test_opcionales_vacios_se_normalizan_a_none(repo):
    empresa = EmpresaService(repo).registrar(uuid4(), "Empresa", "Cali", " \t", "\n ")
    assert empresa.nit is None and empresa.sector is None


def test_limites_inclusivos_se_validan_despues_de_normalizar(repo):
    empresa = EmpresaService(repo).registrar(
        uuid4(), " " + "á" * 150 + " ", " " + "ñ" * 100 + " ",
        " " + "1" * 20 + " ", " " + "é" * 100 + " ",
    )
    assert (len(empresa.nombre), len(empresa.ciudad), len(empresa.nit),
            len(empresa.sector)) == (150, 100, 20, 100)


@pytest.mark.parametrize("campo,valor", [
    ("nombre", "a" * 151), ("ciudad", "a" * 101),
    ("nit", "1" * 21), ("sector", "a" * 101),
    ("nombre", " \t\n"), ("ciudad", " \t\n"),
    ("nombre", None), ("ciudad", None),
    ("nit", 123), ("sector", []),
])
def test_datos_invalidos_no_guardan_empresa(repo, campo, valor):
    datos = dict(nombre="Empresa", ciudad="Bogotá")
    datos[campo] = valor
    with pytest.raises(EmpresaInvalida, match=campo):
        EmpresaService(repo).registrar(uuid4(), **datos)
    assert repo.empresas == {}


@pytest.mark.parametrize("cambios", [
    {"id": "uuid-invalido"}, {"usuario_id": None},
    {"creado_en": datetime(2026, 11, 7)},
])
def test_entidad_impide_identificadores_y_fecha_invalidos(cambios):
    datos = dict(id=uuid4(), usuario_id=uuid4(), nombre="Empresa", ciudad="Cali",
                 creado_en=datetime.now(timezone.utc))
    datos.update(cambios)
    with pytest.raises(ValueError):
        Empresa(**datos)


def test_entidad_normaliza_fecha_a_utc_y_es_inmutable():
    fecha = datetime(2026, 11, 7, 10, tzinfo=timezone(timedelta(hours=-5)))
    empresa = Empresa(uuid4(), uuid4(), " Empresa ", " Cali ", fecha)
    assert empresa.nombre == "Empresa" and empresa.ciudad == "Cali"
    assert empresa.creado_en == datetime(2026, 11, 7, 15, tzinfo=timezone.utc)
    assert empresa.creado_en.tzinfo is timezone.utc
    with pytest.raises(FrozenInstanceError):
        empresa.nombre = "Otra"


def test_consulta_sin_empresa_devuelve_none(repo):
    assert EmpresaService(repo).consultar(uuid4()) is None
    assert repo.empresas == {}


def test_segundo_registro_no_sobrescribe_empresa(repo):
    servicio = EmpresaService(repo)
    usuario_id = uuid4()
    original = servicio.registrar(usuario_id, "Original", "Cali")
    with pytest.raises(EmpresaDuplicada):
        servicio.registrar(usuario_id, "Otra", "Bogotá")
    assert servicio.consultar(usuario_id) is original
    assert len(repo.empresas) == 1


def test_usuarios_aislados_pueden_compartir_nit(repo):
    servicio = EmpresaService(repo)
    primero, segundo = uuid4(), uuid4()
    empresa_a = servicio.registrar(primero, "Empresa A", "Cali", "900123456-7")
    empresa_b = servicio.registrar(segundo, "Empresa B", "Bogotá", "900123456-7")
    assert empresa_a.id != empresa_b.id
    assert servicio.consultar(primero) is empresa_a
    assert servicio.consultar(segundo) is empresa_b
    assert servicio.consultar(uuid4()) is None


def test_colision_al_crear_se_traduce_a_duplicado(repo):
    class RepoColision(CompanyRepositoryFake):
        def buscar_por_usuario(self, usuario_id):
            # Simula una consulta que no vio el registro recién creado.
            return None

    repo = RepoColision()
    servicio = EmpresaService(repo)
    usuario_id = uuid4()
    original = servicio.registrar(usuario_id, "Original", "Cali")
    with pytest.raises(EmpresaDuplicada):
        servicio.registrar(usuario_id, "Otra", "Bogotá")
    assert repo.empresas == {usuario_id: original}


@pytest.mark.parametrize("error", [ValueError("Otro error"), RuntimeError("Fallo de guardado")])
def test_errores_de_repositorio_no_se_confunden_con_duplicidad(error):
    class RepoFalla(CompanyRepositoryFake):
        def crear(self, empresa):
            raise error

    repo = RepoFalla()
    with pytest.raises(type(error)) as resultado:
        EmpresaService(repo).registrar(uuid4(), "Empresa", "Cali")
    assert resultado.value is error
    assert repo.empresas == {}
