#!/usr/bin/env bash
set -Eeuo pipefail

# ContinuitY RF01 BD-06. Sólo validaciones; no modifica archivos ni BD principal.
# Este script debe ejecutarse desde la raíz del repositorio; no seguir el directorio del ZIP.
if [[ ! -f app/main.py || ! -d tests ]]; then
  echo 'ERROR: ejecutar desde la raíz de ~/spartanlab/continuity' >&2
  exit 2
fi

printf '\n=== BD-06 / 1. Estructura e importaciones ===\n'
PYTHONPATH=. python - <<'PY'
from app.core.models import Usuario, Sesion
from app.infrastructure.audit import registrar_evento
from app.infrastructure.postgres_users import PostgresUserRepository
from app.infrastructure.postgres_sessions import PostgresSessionRepository
from app.infrastructure.postgres_connection import nueva_conexion
print('[OK] Módulos RF01 + adaptadores importables')
PY

printf '\n=== BD-06 / 2. Selección de repositorios en memoria ===\n'
CONTINUITY_STORAGE=memory CONTINUITY_ENV=production PYTHONPATH=. python - <<'PY'
from app.main import create_app
app = create_app()
assert type(app.state.usuarios).__name__ == 'MemoryUserRepository'
assert type(app.state.sesiones).__name__ == 'MemorySessionRepository'
assert app.state.secure_cookies is True
print('[OK] Repositorios de memoria y cookie Secure habilitada')
PY

printf '\n=== BD-06 / 3. Regresión automática en memoria ===\n'
CONTINUITY_STORAGE=memory CONTINUITY_ENV=production PYTHONPATH=. python -m pytest -q

printf '\n=== BD-06 / 4. Verificaciones del repositorio (lectura) ===\n'
git status --short
printf '\nArchivos sensibles potencialmente versionados (sólo nombres):\n'
git ls-files --cached | grep -Ei '(^|/)(\.env($|\.)|cookies?\.txt$|.*\.(pem|key|p12|pfx)$|.*secret.*)' || true
printf '\nNOTA: revisar .gitignore y git status antes de hacer commit.\n'
printf '\n[OK] Verificaciones locales finalizadas.\n'
printf 'Pendiente: ejecutar por separado BD-03 y BD-04 en continuity_rf01_test.\n'
