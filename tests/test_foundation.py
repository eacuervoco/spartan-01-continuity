from datetime import datetime, timedelta, timezone
from uuid import uuid4
import pytest
from app.core.auth_service import AuthService
from app.core.models import Credencial, EstadoCuenta, EstadoSesion, Sesion, Usuario
from app.core.repositories import MembershipLookup, SessionRepository, UserRepository
from app.infrastructure.memory import MemorySessionRepository, MemoryUserRepository, NoMembershipLookup

NOW = datetime(2026, 10, 29, 12, tzinfo=timezone.utc)


def cuenta(email="cliente@ejemplo.com"):
    user = Usuario(uuid4(), "Cliente", email, NOW)
    return user, Credencial(user.id, "hash_ficticio_para_pruebas")


def test_usuario_valido_activo_cliente():
    usuario, credencial = cuenta()
    assert usuario.estado == EstadoCuenta.ACTIVA
    assert usuario.rol == "CLIENTE"
    assert credencial.usuario_id == usuario.id


def test_no_existe_no_es_estado_persistible():
    with pytest.raises(ValueError):
        Usuario(uuid4(), "Cliente", "a@b.co", NOW, estado=EstadoCuenta.NO_EXISTE)


def test_cuenta_inexistente_y_activa():
    repo, sesiones = MemoryUserRepository(), MemorySessionRepository()
    servicio = AuthService(repo, sesiones)
    assert servicio.estado_cuenta("ninguno@ejemplo.com") == EstadoCuenta.NO_EXISTE
    user, credential = cuenta()
    repo.crear_cuenta(user, credential)
    assert servicio.estado_cuenta(user.email_normalizado) == EstadoCuenta.ACTIVA


def test_registro_dual_sin_parcialidad_si_ids_no_coinciden():
    repo = MemoryUserRepository()
    user, _ = cuenta()
    with pytest.raises(ValueError):
        repo.crear_cuenta(user, Credencial(uuid4(), "hash"))
    assert repo.buscar_por_correo(user.email_normalizado) is None
    assert repo.buscar_credencial(user.id) is None


def test_correo_duplicado_no_sobrescribe_credencial():
    repo = MemoryUserRepository()
    user, credencial = cuenta()
    repo.crear_cuenta(user, credencial)
    otro, otra_credencial = cuenta()
    with pytest.raises(ValueError):
        repo.crear_cuenta(otro, otra_credencial)
    assert repo.buscar_credencial(user.id) == credencial
    assert repo.buscar_credencial(otro.id) is None


def test_sesion_vigente_y_expirada():
    user, _ = cuenta()
    sesion = Sesion("token-opaco-de-prueba", user.id, NOW, NOW + timedelta(hours=8), NOW)
    repo = MemorySessionRepository()
    repo.guardar(sesion)
    servicio = AuthService(MemoryUserRepository(), repo)
    assert servicio.estado_sesion(sesion.id, NOW) == EstadoSesion.VIGENTE
    assert servicio.estado_sesion(sesion.id, NOW + timedelta(hours=8)) == EstadoSesion.EXPIRADA


def test_invalidacion_impide_reutilizacion():
    repo = MemorySessionRepository()
    uid = uuid4()
    repo.guardar(Sesion("abc", uid, NOW, NOW + timedelta(hours=1), NOW))
    repo.invalidar("abc")
    assert AuthService(MemoryUserRepository(), repo).estado_sesion("abc", NOW) == EstadoSesion.EXPIRADA


def test_fechas_sin_zona_horaria_se_rechazan():
    with pytest.raises(ValueError):
        Usuario(uuid4(), "Cliente", "a@b.co", datetime(2026, 1, 1))


def test_contratos_y_autorizacion_cerrada():
    usuarios, sesiones, membresia = MemoryUserRepository(), MemorySessionRepository(), NoMembershipLookup()
    assert isinstance(usuarios, UserRepository)
    assert isinstance(sesiones, SessionRepository)
    assert isinstance(membresia, MembershipLookup)
    assert not membresia.tiene_asociacion_autorizada(uuid4())
