"""Límite provisional por proceso; requiere almacenamiento compartido en producción."""
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from threading import RLock


class DemasiadosIntentos(Exception):
    pass


class MemoryLoginLimiter:
    """Cinco fallos por IP y por identidad dentro de 15 minutos; falla cerrada."""
    def __init__(self, max_fallos: int = 5, ventana_minutos: int = 15) -> None:
        self.max_fallos = max_fallos
        self.ventana = timedelta(minutes=ventana_minutos)
        self._fallos: dict[str, deque[datetime]] = defaultdict(deque)
        self._lock = RLock()

    def _limpiar(self, clave: str, ahora: datetime) -> None:
        cola = self._fallos[clave]
        while cola and cola[0] <= ahora - self.ventana:
            cola.popleft()

    def verificar(self, ip: str, correo: str) -> None:
        ahora = datetime.now(timezone.utc)
        with self._lock:
            for clave in (f"ip:{ip}", f"correo:{correo.strip().casefold()}"):
                self._limpiar(clave, ahora)
                if len(self._fallos[clave]) >= self.max_fallos:
                    raise DemasiadosIntentos()

    def fallo(self, ip: str, correo: str) -> None:
        ahora = datetime.now(timezone.utc)
        with self._lock:
            for clave in (f"ip:{ip}", f"correo:{correo.strip().casefold()}"):
                self._limpiar(clave, ahora)
                self._fallos[clave].append(ahora)

    def exito(self, ip: str, correo: str) -> None:
        # No se borran fallos de IP (evita que una cuenta válida elimine el límite).
        with self._lock:
            self._fallos.pop(f"correo:{correo.strip().casefold()}", None)
