"""Repositorio de sesiones PostgreSQL para ContinuitY RF01 (Psycopg 3).

Requiere database/003_sesiones_revocacion.sql.
No persiste tokens en claro: solo SHA-256. Mantiene tombstones para
que una sesión revocada no vuelva a autorizarse con un UPSERT concurrente.
"""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from hashlib import sha256

from psycopg import Connection

from app.core.models import Sesion
from app.core.session_service import SesionNoVigente


class PostgresSessionRepository:
    def __init__(self, connect: Callable[[], Connection]) -> None:
        self._connect = connect

    @staticmethod
    def _digest(token: str) -> str:
        return sha256(token.encode("utf-8")).hexdigest()

    def guardar(self, sesion: Sesion) -> None:
        digest = self._digest(sesion.id)
        with self._connect() as conn:
            with conn.cursor() as cur:
                # Si ya existe, solo actualiza la actividad. Una fila revocada
                # permanece revocada y jamás es reinsertada por un UPSERT.
                cur.execute(
                    """INSERT INTO public.sesiones
                       (token_digest, usuario_id, creado_en, expira_en, ultima_actividad_en)
                       VALUES (%s, %s, %s, %s, %s)
                       ON CONFLICT (token_digest) DO UPDATE
                       SET ultima_actividad_en = GREATEST(
                           sesiones.ultima_actividad_en, EXCLUDED.ultima_actividad_en
                       )
                       WHERE sesiones.revocada_en IS NULL
                         AND sesiones.usuario_id = EXCLUDED.usuario_id
                         AND sesiones.creado_en = EXCLUDED.creado_en
                         AND sesiones.expira_en = EXCLUDED.expira_en
                       RETURNING token_digest""",
                    (digest, sesion.usuario_id, sesion.creado_en,
                     sesion.expira_en, sesion.ultima_actividad_en),
                )
                if cur.fetchone() is None:
                    raise SesionNoVigente()

    def buscar(self, token: str) -> Sesion | None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT usuario_id, creado_en, expira_en, ultima_actividad_en
                       FROM public.sesiones
                       WHERE token_digest = %s AND revocada_en IS NULL""",
                    (self._digest(token),),
                )
                row = cur.fetchone()
        if row is None:
            return None
        return Sesion(
            id=token, usuario_id=row[0], creado_en=row[1],
            expira_en=row[2], ultima_actividad_en=row[3],
        )

    def invalidar(self, token: str) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """UPDATE public.sesiones SET revocada_en = %s
                       WHERE token_digest = %s AND revocada_en IS NULL""",
                    (datetime.now(timezone.utc), self._digest(token)),
                )
