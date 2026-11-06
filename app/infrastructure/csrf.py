"""Token CSRF ligado a la sesión, con HMAC y clave efímera por proceso."""
import hashlib
import hmac
import secrets


class CsrfProtector:
    def __init__(self):
        self._clave = secrets.token_bytes(32)

    def token(self, session_id: str) -> str:
        return hmac.new(self._clave, session_id.encode(), hashlib.sha256).hexdigest()

    def valido(self, session_id: str, provided: str | None) -> bool:
        return bool(provided) and hmac.compare_digest(self.token(session_id), provided)
