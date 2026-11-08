# ContinuitY V3.0 — RF01 | Autenticación y persistencia PostgreSQL

**Estado:** MVP RF01 funcional y validado
**Arquitectura:** Monolito modular de tres capas
**Tecnologías:** Python 3.12 · FastAPI · PostgreSQL 17 · Psycopg 3 · HTML5 · CSS3 · JavaScript

## 1. Descripción

ContinuitY es una plataforma de consultoría tecnológica asistida por inteligencia artificial, orientada a identificar oportunidades de optimización y aprovechamiento de infraestructura tecnológica en pequeñas y medianas empresas.

El **RF01 — Registro e inicio de sesión** implementa el acceso inicial a la plataforma, permitiendo crear cuentas, autenticar usuarios, administrar sesiones y consultar el contexto de acceso empresarial.

La solución cuenta con persistencia PostgreSQL, validación de credenciales, protección de sesiones y pruebas automatizadas.

## 2. Arquitectura

Se implementa un **monolito modular de tres capas**, aplicando programación orientada a objetos (POO), separación de responsabilidades y los patrones Repository, Service Layer y Dependency Injection.

```text
app/
├── api/                # Presentación: endpoints HTTP
├── core/               # Dominio, modelos y servicios
├── infrastructure/     # Seguridad y persistencia
├── static/             # CSS y JavaScript
├── templates/          # HTML
└── main.py             # Composición de dependencias

database/
├── 001_schema.sql
├── 002_permisos.sql
└── 003_sesiones_revocacion.sql

tests/                  # Pruebas unitarias y de integración
scripts/                # Validaciones operativas
```

La capa de dominio es independiente de FastAPI y PostgreSQL.

## 3. Funcionalidades implementadas

- Registro de usuarios con persistencia PostgreSQL.
- Normalización y unicidad del correo electrónico.
- Almacenamiento seguro de contraseñas mediante Argon2id.
- Inicio de sesión con tokens opacos.
- Cookies HttpOnly, Secure en producción y SameSite=Lax.
- Protección CSRF para cierre de sesión.
- Control de intentos de autenticación.
- Sesiones con expiración por inactividad de 30 minutos y límite absoluto de 8 horas.
- Invalidación definitiva de sesiones.
- Consulta del contexto del usuario autenticado.
- Control de acceso empresarial con autorización restrictiva por defecto.

**Estados de cuenta:** `ACTIVA`, `NO EXISTE` (resultado de consulta, no persistido).

**Estados de sesión:** `VIGENTE`, `EXPIRADA`.

## 4. Persistencia PostgreSQL

El sistema permite seleccionar el almacenamiento mediante `CONTINUITY_STORAGE`:

| Valor | Descripción |
|---|---|
| `memory` | Repositorios en memoria para pruebas |
| `postgres` | Persistencia real mediante Psycopg 3 |

### Modelo de datos

- `usuarios`: datos de identificación, correo normalizado, estado y rol.
- `credenciales`: hash Argon2id asociado al usuario.
- `sesiones`: digest SHA-256 del token, fechas de actividad, expiración y revocación.

El registro de usuario y credencial es transaccional. PostgreSQL impone restricciones de unicidad e integridad referencial.

La infraestructura PostgreSQL está alojada en SpartanLab y se accede desde WSL mediante un túnel SSH, sin exponer el puerto de la base de datos directamente a la red.

## 5. Instalación

Desde la raíz del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
```

### Ejecución con almacenamiento en memoria

```bash
CONTINUITY_STORAGE=memory \
CONTINUITY_ENV=development \
python -m uvicorn app.main:app --reload
```

### Ejecución con PostgreSQL

Requiere PostgreSQL configurado, el esquema SQL aplicado y el túnel SSH activo.

```bash
export CONTINUITY_STORAGE=postgres
export CONTINUITY_ENV=development

export CONTINUITY_DB_HOST=127.0.0.1
export CONTINUITY_DB_PORT=15432
export CONTINUITY_DB_NAME=continuity_db
export CONTINUITY_DB_USER=continuity_app

read -rs -p "Contraseña PostgreSQL: " CONTINUITY_DB_PASSWORD
echo
export CONTINUITY_DB_PASSWORD

python -m uvicorn app.main:app \
  --host 127.0.0.1 --port 8000
```

`CONTINUITY_ENV=development` se utiliza únicamente para pruebas locales mediante HTTP. Los despliegues reales requieren HTTPS y cookies Secure.

Las migraciones SQL se ejecutan explícitamente, con una cuenta administrativa autorizada. FastAPI no crea tablas durante su arranque.

## 6. Acceso y recorrido funcional

Abrir:

`http://127.0.0.1:8000/login`

**Flujo de validación:**

1. Crear una cuenta desde `/register`.
2. Iniciar sesión desde `/login`.
3. Acceder a `/access` y consultar el contexto.
4. Confirmar el destino `INCORPORACION_EMPRESARIAL`, cuando no existe una membresía autorizada.
5. Obtener el token CSRF y cerrar sesión.
6. Verificar que una sesión invalidada no permite acceder nuevamente.
7. Reiniciar FastAPI y comprobar que el usuario registrado continúa disponible en PostgreSQL.

### Endpoints principales

| Método | Endpoint | Función |
|---|---|---|
| POST | `/auth/register` | Registro de cuenta |
| POST | `/auth/login` | Inicio de sesión |
| GET | `/auth/session` | Consulta de sesión |
| GET | `/auth/me` | Contexto del usuario |
| GET | `/auth/csrf` | Token CSRF |
| POST | `/auth/logout` | Cierre de sesión |

## 7. Pruebas y calidad

### Regresión del backend

```bash
CONTINUITY_STORAGE=memory \
CONTINUITY_ENV=production \
python -m pytest -q
```

**Último resultado validado:**

```text
66 passed, 1 warning in 17.03s
```

La advertencia corresponde a una deprecación de Starlette relacionada con `httpx`.

### Integración PostgreSQL

Las pruebas de integración utilizan la base aislada `continuity_rf01_test`.

```bash
PYTHONPATH=. python tests/test_bd03_integracion.py

PYTHONPATH=. python tests/test_bd04_integracion.py
```

**Resultados verificados:**

- BD-03: registro, persistencia, duplicados, integridad y rollback aprobados.
- BD-04: sesiones, reconexión, actualización de actividad, logout irreversible y expiraciones aprobados.
- BD-05: registro, autenticación y consulta de usuarios desde el frontend con PostgreSQL real.
- BD-06: regresión de 66 pruebas y revisión básica de seguridad aprobadas.

## 8. Seguridad

Se implementan controles básicos y efectivos:

- Contraseñas protegidas mediante Argon2id.
- Consultas SQL parametrizadas.
- Credenciales PostgreSQL mediante variables de entorno.
- Tokens de sesión no almacenados en texto claro en PostgreSQL.
- Protección CSRF y verificación de origen.
- Restricciones de integridad en base de datos.
- Acceso empresarial restrictivo por defecto.
- Exclusión de `.env` y `cookies.txt` mediante `.gitignore`.

## 9. Limitaciones del MVP

- No incluye recuperación de contraseñas, OAuth ni MFA.
- RF02 implementa registro y consulta de una empresa por usuario. Las membresías empresariales siguen sin implementarse.
- No incluye panel empresarial funcional.
- No incorpora agentes autónomos ni integración de inteligencia artificial en RF01.
- No implementa monitoreo continuo ni descubrimiento automático de infraestructura.
- La gestión avanzada de disponibilidad del túnel SSH queda fuera de esta fase.
- La auditoría manual WCAG y las pruebas automatizadas en navegadores reales continúan pendientes.

## 10. Estado y continuidad

**RF01:** registro, autenticación, sesiones y contexto de acceso implementados con persistencia PostgreSQL.

**Próximo paso:** cierre de versionamiento Git y continuación incremental de los requisitos funcionales de ContinuitY.

---

**Proyecto:** ContinuitY V3.0
**Entorno de desarrollo:** SpartanLab
**Principio de ingeniería:** simplicidad, modularidad, seguridad básica efectiva y validación continua.

## 11. Portal académico V3.0 · RF01 y RF02

El [portal estático](docs/index.html) presenta exclusivamente RF01 — Registro, autenticación y gestión de sesiones y RF02 — Registro y asociación de empresa. Cada ficha contiene exactamente seis apartados: requisito, historia de usuario, matriz de aceptación, ciclo de vida, prototipo interactivo y evaluación. El diseño PostgreSQL se integra en D de ambos RF; los controles de seguridad, en D de RF01. Se conserva la identidad visual del frontend, sin frameworks ni dependencias nuevas.

El MVP de ContinuitY tiene previsto alcanzar el diagnóstico técnico de infraestructura tecnológica y la interacción con un modelo de inteligencia artificial, para identificar riesgos, activos subutilizados y oportunidades de optimización. RF01 y RF02 proporcionan la base de identidad y registro empresarial. El diagnóstico y la integración de IA pertenecen a incrementos posteriores y no se consideran implementados en esta entrega.

RF02 está integrado en `main`, en `1f858c0`. Las cifras de pruebas anteriores de este README y `README_RF01.md` pertenecen al cierre histórico de RF01. Las [fuentes vigentes](docs/evidence/sources.md) distinguen documentos históricos de implementación. El [registro actual](docs/evidence/revision.md) conserva resultados, advertencias y omisiones: 131 pruebas pytest aprobadas y 8 PostgreSQL omitidas; 19 pruebas JS del frontend aprobadas. Los scripts manuales BD-03/BD-04 no fueron ejecutados por pytest.

Para consultar localmente:

```bash
python3 -m http.server 8080 --directory docs
```

Abrir `http://localhost:8080`. Para comprobar el alcance vigente:

```bash
python3 docs/checks/validate-rf01-rf02.py
node tests/frontend_rf02.test.cjs
.venv/bin/python -m pytest -ra
git diff --check
```

Las comprobaciones antiguas `docs/checks/portal.test.cjs` y `validate.py` se conservan intactas: esperan doce fichas, siete apartados y rutas retiradas; sus fallos se registran, no se ocultan. La validación vigente está en archivos nuevos y comprueba el alcance pedido, el flujo simulado, evaluación local, rutas relativas, labels, H1 y SVG. El DOM simulado no sustituye revisión visual ni WCAG.

GitHub Pages: Settings → Pages → Build and deployment → Deploy from a branch → `main` → `/docs` → Save. `docs/.nojekyll`, assets locales y navegación por fragmentos permiten servir el portal bajo la ruta del repositorio. Tras revisar y autorizar commit y push, publicar estos cambios en `main` y consultar la URL que Pages devuelva. En esta revisión no se hicieron commits, fusiones ni push, ni se verificó o cambió la configuración remota de Pages.

La demo no llama a APIs ni PostgreSQL. Usa datos ficticios y una clave pública de práctica de solo lectura; permite provocar casos inválidos sin solicitar contraseñas reales. Su información desaparece al recargar. Las evaluaciones docentes empiezan Sin evaluar, se guardan solo en el navegador y permiten descargar JSON e imprimir. Persistencia PostgreSQL, revisión visual/móvil, accesibilidad manual y evaluación docente quedan pendientes. No hay simulación de diagnóstico ni IA.
