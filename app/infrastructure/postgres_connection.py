"""Fábrica sencilla de conexiones PostgreSQL para los repositorios RF01."""

import os

import psycopg


def nueva_conexion():
    """Abre una conexión por operación; no almacena contraseñas en el código."""
    # Estas cuatro variables deben estar definidas cuando se active PostgreSQL.
    required = (
        "CONTINUITY_DB_HOST",
        "CONTINUITY_DB_PORT",
        "CONTINUITY_DB_NAME",
        "CONTINUITY_DB_USER",
        "CONTINUITY_DB_PASSWORD",
    )
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError("Configuración PostgreSQL incompleta")
    return psycopg.connect(
        host=os.environ["CONTINUITY_DB_HOST"],
        port=int(os.environ["CONTINUITY_DB_PORT"]),
        dbname=os.environ["CONTINUITY_DB_NAME"],
        user=os.environ["CONTINUITY_DB_USER"],
        password=os.environ["CONTINUITY_DB_PASSWORD"],
        connect_timeout=5,
    )
