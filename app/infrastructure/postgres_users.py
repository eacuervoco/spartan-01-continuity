"""Adaptador PostgreSQL del repositorio de usuarios de ContinuitY RF01.

Ubicación recomendada: app/infrastructure/postgres_users.py.
No altera los servicios, las rutas ni los repositorios en memoria.
"""

from __future__ import annotations

from collections.abc import Callable
from uuid import UUID

import psycopg
from psycopg import Connection, errors

from app.core.models import Credencial, EstadoCuenta, Usuario


class PostgresUserRepository:
    """Implementa UserRepository con una conexión por operación.

    ``connect`` es una fábrica de conexiones configurable, permitiendo
    inyectar conexiones de una BD de pruebas separada.
    """

    def __init__(self, connect: Callable[[], Connection]) -> None:
        self._connect = connect

    @staticmethod
    def _usuario(row: tuple | None) -> Usuario | None:
        if row is None:
            return None
        return Usuario(
            id=row[0],
            nombre=row[1],
            email_normalizado=row[2],
            creado_en=row[3],
            estado=EstadoCuenta(row[4]),
            rol=row[5],
        )

    def buscar_por_correo(self, email_normalizado: str) -> Usuario | None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT id, nombre, email_normalizado, creado_en, estado, rol
                       FROM public.usuarios WHERE email_normalizado = %s""",
                    (email_normalizado,),
                )
                return self._usuario(cur.fetchone())

    def buscar_por_id(self, usuario_id: UUID) -> Usuario | None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT id, nombre, email_normalizado, creado_en, estado, rol
                       FROM public.usuarios WHERE id = %s""",
                    (usuario_id,),
                )
                return self._usuario(cur.fetchone())

    def buscar_credencial(self, usuario_id: UUID) -> Credencial | None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT usuario_id, password_hash
                       FROM public.credenciales WHERE usuario_id = %s""",
                    (usuario_id,),
                )
                row = cur.fetchone()
                return Credencial(usuario_id=row[0], password_hash=row[1]) if row else None

    def crear_cuenta(self, usuario: Usuario, credencial: Credencial) -> None:
        if usuario.id != credencial.usuario_id:
            raise ValueError("La credencial no pertenece al usuario")

        try:
            # El contexto confirma la transacción solo si ambas inserciones
            # terminan correctamente; ante cualquier error hace ROLLBACK.
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO public.usuarios
                           (id, nombre, email_normalizado, creado_en, estado, rol)
                           VALUES (%s, %s, %s, %s, %s, %s)""",
                        (
                            usuario.id,
                            usuario.nombre,
                            usuario.email_normalizado,
                            usuario.creado_en,
                            usuario.estado.value,
                            usuario.rol,
                        ),
                    )
                    cur.execute(
                        """INSERT INTO public.credenciales
                           (usuario_id, password_hash) VALUES (%s, %s)""",
                        (credencial.usuario_id, credencial.password_hash),
                    )
        except errors.UniqueViolation as exc:
            # Contrato que RegistroService ya traduce a CorreoDuplicado.
            # No exponer valores o detalles internos del motor.
            raise ValueError("Cuenta duplicada") from exc
