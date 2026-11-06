"""Defensa básica frente a solicitudes cross-site que cambian estado."""
from urllib.parse import urlsplit
from fastapi import HTTPException, Request


def verificar_origen(request: Request) -> None:
    if request.headers.get("sec-fetch-site", "").lower() == "cross-site":
        raise HTTPException(status_code=403, detail="Origen no autorizado")
    origin = request.headers.get("origin")
    if origin:
        parsed = urlsplit(origin)
        expected = urlsplit(str(request.base_url))
        if parsed.scheme not in ("http", "https") or (parsed.scheme, parsed.netloc) != (expected.scheme, expected.netloc):
            raise HTTPException(status_code=403, detail="Origen no autorizado")
