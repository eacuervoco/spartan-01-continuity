"""Almacenamiento temporal para pruebas y fase backend; no apto para producción."""
from threading import RLock
from uuid import UUID
from app.core.models import Credencial, Empresa, Sesion, Usuario


class MemoryUserRepository:
    def __init__(self) -> None:
        self._lock = RLock()
        self._usuarios: dict[UUID, Usuario] = {}
        self._por_correo: dict[str, UUID] = {}
        self._credenciales: dict[UUID, Credencial] = {}

    def buscar_por_correo(self, email_normalizado: str) -> Usuario | None:
        uid = self._por_correo.get(email_normalizado)
        return self._usuarios.get(uid) if uid is not None else None

    def buscar_por_id(self, usuario_id: UUID) -> Usuario | None:
        return self._usuarios.get(usuario_id)

    def buscar_credencial(self, usuario_id: UUID) -> Credencial | None:
        return self._credenciales.get(usuario_id)

    def crear_cuenta(self, usuario: Usuario, credencial: Credencial) -> None:
        # Un mismo proceso evita carreras entre verificación y almacenamiento.
        with self._lock:
            if usuario.id != credencial.usuario_id:
                raise ValueError("La credencial no pertenece al usuario")
            if usuario.id in self._usuarios or usuario.email_normalizado in self._por_correo:
                raise ValueError("Cuenta duplicada")
            # Copias locales: solo se publica el estado conjunto al finalizar.
            usuarios = {**self._usuarios, usuario.id: usuario}
            por_correo = {**self._por_correo, usuario.email_normalizado: usuario.id}
            credenciales = {**self._credenciales, usuario.id: credencial}
            self._usuarios, self._por_correo, self._credenciales = usuarios, por_correo, credenciales


class MemorySessionRepository:
    def __init__(self) -> None:
        self._sesiones: dict[str, Sesion] = {}

    def guardar(self, sesion: Sesion) -> None:
        self._sesiones[sesion.id] = sesion

    def buscar(self, token: str) -> Sesion | None:
        return self._sesiones.get(token)

    def invalidar(self, token: str) -> None:
        self._sesiones.pop(token, None)


class MemoryCompanyRepository:
    def __init__(self) -> None:
        self._lock = RLock()
        self._empresas: dict[UUID, Empresa] = {}

    def buscar_por_usuario(self, usuario_id: UUID) -> Empresa | None:
        with self._lock:
            return self._empresas.get(usuario_id)

    def crear(self, empresa: Empresa) -> None:
        with self._lock:
            if empresa.usuario_id in self._empresas:
                raise ValueError("Empresa duplicada")
            self._empresas[empresa.usuario_id] = empresa


class NoMembershipLookup:
    """Fallo cerrado: nadie obtiene autorización empresarial por defecto."""
    def tiene_asociacion_autorizada(self, usuario_id: UUID) -> bool:
        return False
