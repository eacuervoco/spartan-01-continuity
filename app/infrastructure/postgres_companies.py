"""Repositorio RF02: conexión por operación y transacciones Psycopg existentes."""
from collections.abc import Callable
from uuid import UUID

from psycopg import Connection, errors

from app.core.models import Empresa


class PostgresCompanyRepository:
    def __init__(self, connect: Callable[[], Connection]) -> None:
        self._connect = connect

    def buscar_por_usuario(self, usuario_id: UUID) -> Empresa | None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT id, usuario_id, nombre, ciudad, creado_en, nit, sector
                       FROM public.empresas WHERE usuario_id = %s""",
                    (usuario_id,),
                )
                row = cur.fetchone()
        return Empresa(*row) if row is not None else None

    def crear(self, empresa: Empresa) -> None:
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO public.empresas
                           (id, usuario_id, nombre, ciudad, creado_en, nit, sector)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        (empresa.id, empresa.usuario_id, empresa.nombre, empresa.ciudad,
                         empresa.creado_en, empresa.nit, empresa.sector),
                    )
        except errors.UniqueViolation as exc:
            if (exc.diag.constraint_name == "empresas_usuario_id_key"
                    and exc.diag.table_name == "empresas"
                    and exc.diag.schema_name == "public"):
                raise ValueError("Empresa duplicada") from exc
            raise
