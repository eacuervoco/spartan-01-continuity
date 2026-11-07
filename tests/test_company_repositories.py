"""Adaptadores RF02 con dobles: no requieren conexiones PostgreSQL."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Barrier
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from psycopg import errors

from app.core.models import Empresa
from app.core.repositories import CompanyRepository
from app.infrastructure.memory import MemoryCompanyRepository
from app.infrastructure.postgres_companies import PostgresCompanyRepository


def empresa():
    return Empresa(uuid4(), uuid4(), "Empresa", "Cali", datetime.now(timezone.utc))


@pytest.mark.parametrize("restriccion,tabla,esquema,duplicado", [
    ("empresas_usuario_id_key", "empresas", "public", True),
    ("empresas_pkey", "empresas", "public", False),
    ("empresas_usuario_id_key", "otra", "public", False),
    ("empresas_usuario_id_key", "empresas", "otro", False),
])
def test_traduce_solo_unique_del_usuario(restriccion, tabla, esquema, duplicado):
    class Colision(errors.UniqueViolation):
        @property
        def diag(self):
            resultado = MagicMock()
            resultado.constraint_name = restriccion
            resultado.table_name = tabla
            resultado.schema_name = esquema
            return resultado

    error = Colision("detalle interno")
    conectar = MagicMock()
    conectar.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value.execute.side_effect = error
    repo = PostgresCompanyRepository(conectar)
    with pytest.raises(ValueError if duplicado else Colision) as resultado:
        repo.crear(empresa())
    if duplicado:
        assert str(resultado.value) == "Empresa duplicada" and resultado.value.__cause__ is error
    else:
        assert resultado.value is error


def test_consulta_recupera_empresa_y_ausencia():
    original = empresa()
    conectar = MagicMock()
    cursor = conectar.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = (original.id, original.usuario_id, original.nombre,
                                   original.ciudad, original.creado_en, original.nit, original.sector)
    repo = PostgresCompanyRepository(conectar)
    assert isinstance(repo, CompanyRepository)
    assert repo.buscar_por_usuario(original.usuario_id) == original
    cursor.fetchone.return_value = None
    assert repo.buscar_por_usuario(uuid4()) is None


def test_memory_creacion_simultanea_no_sobrescribe():
    from dataclasses import replace

    repo = MemoryCompanyRepository()
    assert isinstance(repo, CompanyRepository)
    primera = empresa()
    segunda = replace(primera, id=uuid4(), nombre="Otra")
    barrera = Barrier(2)

    def crear(valor):
        barrera.wait(timeout=10)
        try:
            repo.crear(valor)
            return valor
        except ValueError as exc:
            assert str(exc) == "Empresa duplicada"
            return None

    with ThreadPoolExecutor(max_workers=2) as executor:
        resultados = list(executor.map(crear, [primera, segunda]))
    ganadoras = [r for r in resultados if r is not None]
    assert len(ganadoras) == 1
    assert repo.buscar_por_usuario(primera.usuario_id) == ganadoras[0]
