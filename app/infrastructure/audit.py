"""Auditoría HTTP mínima sin datos personales, cookies ni credenciales."""
import logging
from fastapi import Request

LOGGER = logging.getLogger("continuity.audit")

EVENTOS = {
    ("POST", "/auth/register"): "registro",
    ("POST", "/auth/login"): "inicio_sesion",
    ("POST", "/auth/logout"): "cierre_sesion",
}


def registrar_evento(request: Request, estado_http: int) -> None:
    evento = EVENTOS.get((request.method, request.url.path))
    if evento is None:
        return
    # Datos deliberadamente acotados: nunca correo, IP, headers, cuerpo ni token.
    LOGGER.info("evento=%s resultado=%s codigo_http=%d", evento,
                "exitoso" if 200 <= estado_http < 300 else "fallido", estado_http)
