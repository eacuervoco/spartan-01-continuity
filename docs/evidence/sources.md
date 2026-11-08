# Fuentes vigentes y trazabilidad

Revisión: 7 de noviembre de 2026, America/Bogota. Base local: `main`, `1f858c0`, merge de RF02. Código, migraciones y pruebas existentes se leyeron sin modificarlos. Las rutas `app/`, `database/` y `tests/` citadas son rutas del repositorio, no endpoints de GitHub Pages.

## Precedencia

El comportamiento implementado se determina por código y pruebas de `main`; las restricciones de PostgreSQL, por sus migraciones y adaptadores. La ejecución se acredita únicamente con el [registro de revisión](revision.md).

`CONTINUITY_RF02_REGISTRO_EMPRESA.md` describe empresa por usuario; sus rutas propuestas se concretaron como `/auth/companies` y `/auth/companies/me`. `README_RF01.md` y `FRONTEND_F01.md` reflejan etapas anteriores: memoria y login solo visual, respectivamente. No prevalecen sobre el código actual. Las limitaciones históricas del README que negaban empresas se corrigieron.

Los documentos F0 de `docs/requirements/`, `project-management/`, `architecture/` y `uml/` se conservan como antecedentes, fuera de la presentación evaluable. Su numeración RF-01 diagnóstico y RF-02 evidencia técnica no corresponde a RF01 identidad y RF02 empresa. No se usa su declaración de baseline para afirmar aprobación de esta entrega. No se crean equivalencias ni fichas de requisitos futuros, ni cronogramas o resultados de sprints.

Las historias HU-RF01-01 y HU-RF02-01 y sus matrices son síntesis académicas de esta revisión. Los identificadores de criterios pertenecen a estas matrices, no renumeran los criterios históricos ni certifican aceptación docente.

## RF01

Implementación: `app/core/registration.py`, `login.py`, `session_service.py`, `access_service.py`, `models.py`; `app/api/auth.py`, `session.py`, `access.py`; adaptadores de usuarios y sesiones.

Consultar los [extractos de implementación](implementation.md) con números de línea originales y el [índice de pruebas](test-index.md), con nombres exactos usados en C. Los [extractos de pruebas](test-excerpts.md) muestran los escenarios y aserciones originales. Evidencias principales: `tests/test_registration.py`, `test_login.py`, `test_sessions.py`, `test_access.py`, `test_quality.py`. La prueba de registro comprueba Argon2id, respuesta sin contraseña y ausencia de inicio automático de sesión. Las de sesiones comprueban los límites exactos de 30 minutos y 8 horas, logout, CSRF y origen.

`tests/test_bd03_integracion.py` y `test_bd04_integracion.py` contienen funciones `main()` para ejecución manual en una base dedicada; pytest no ejecuta sus comprobaciones de PostgreSQL. No se ejecutaron aquí. El digest y la revocación persistidos se acreditan por inspección del adaptador, no por una integración aprobada en esta revisión.

## RF02

Implementación: `app/core/models.py`, `company_service.py`, `app/api/companies.py`, `app/infrastructure/postgres_companies.py`, `memory.py`, `database/004_empresas.sql` y composición en `app/main.py`.

Los [extractos](implementation.md) permiten revisar entidad, reglas, contrato y consultas. El [índice de pruebas](test-index.md) permite localizar cada escenario de la matriz: normalización, límites, opcionales nulos, usuario_id rechazado, aislamiento, duplicado, sesiones inválidas, origen, CSRF y fallo interno. `tests/test_companies_api.py` usa sesiones y defensas reales de FastAPI con almacenamiento en memoria, no PostgreSQL.

`tests/test_company_service.py` verifica además fechas UTC, límites inclusivos, usuarios distintos con el mismo NIT y conservación del registro ante duplicados. `tests/test_company_repositories.py` cubre contratos y colisiones con dobles; no sustituye la base real. Las ocho pruebas de `tests/test_postgres_companies.py` quedaron omitidas.

## Diseno

Esquema: `database/001_schema.sql`, `003_sesiones_revocacion.sql`, `004_empresas.sql`. Permisos: `002_permisos.sql`. Revisar sus [extractos íntegros](implementation.md), el [SVG local](../assets/data-model.svg) y la [fuente Mermaid](../assets/data-model.mmd). El SVG es una representación manual de las mismas entidades y cardinalidades, sin servicio de renderizado externo.

Son cuatro tablas: usuarios, credenciales, sesiones y empresas. La FK de credenciales es también su PK: cada usuario puede tener 0..1 credencial en SQL; crear_cuenta inserta ambas filas en una transacción. Usuarios tiene 0..N sesiones y 0..1 empresa. Las dependencias de credenciales y sesiones usan CASCADE; empresas usa RESTRICT y UNIQUE(usuario_id). NIT no tiene UNIQUE. Fechas de sesiones deben respetar creado_en ≤ ultima_actividad_en ≤ expira_en y expira_en > creado_en. revocada_en es opcional.

Los contextos Psycopg confirman cada operación si termina correctamente y revierten ante excepción. El registro de cuenta agrupa sus dos INSERT; el control UNIQUE protege colisiones entre registros empresariales concurrentes. No se infiere aislamiento serializable ni se acredita una prueba concurrente real: la prueba PostgreSQL correspondiente quedó omitida. El backend usa memoria por defecto y permite seleccionar PostgreSQL explícitamente. No se ejecutaron migraciones ni se inspeccionó una base desplegada.

## Seguridad

La tabla de D/RF01 cita los controles encontrados. Sus implementaciones están disponibles en los [extractos locales](implementation.md); los casos automatizados se localizan en el [índice](test-index.md) y sus resultados en la [revisión](revision.md).

Argon2id, correo normalizado, token opaco, digest SHA-256 en PostgreSQL, cookies, HMAC de CSRF, origen, limitador y expiración se documentan con su alcance real. La inspección SQL verifica parámetros separados de las consultas, no inmunidad general ante inyección. La dependencia de sesión protege las rutas privadas existentes; no es un middleware universal de denegación para rutas futuras. `NoMembershipLookup` mantiene restringido el destino por defecto: registrar una empresa no activa un panel ni una membresía.

Pendientes identificados en código: limitador compartido entre procesos, revisión de REVOKE y permisos previos (002 no revoca), configuración HTTPS de producción y validación de persistencia/revocación reales. No hay auditoría de penetración ni certificación de seguridad acreditadas.

## Frontend y demostracion

Se conservaron paleta verde/naranja, marca, tipografía de sistema, tarjetas, foco y formularios del portal existente, derivados de `app/static/css/base.css`, `login.css` y `company.css`. Se contrastaron etiquetas y flujo con `app/templates/{register,login,access}.html` y `app/static/js/{register,login,access}.js`. El frontend real crea la cuenta sin iniciar sesión y muestra Mi empresa desde Mi acceso; el portal reproduce ese recorrido con datos ficticios.

Diferencias deliberadas y visibles: clave de práctica pública y campos de clave de solo lectura con controles para casos inválidos; correo de dominios example; expiración manual; comprobación didáctica de duplicidad. El portal no reproduce red, cookies, CSRF, temporizadores, fallos de servidor ni concurrencia. No hace peticiones al backend y los datos de práctica no se guardan en localStorage. Solo la evaluación docente se conserva localmente y puede descargarse o imprimirse.

La revisión visual en navegador, móvil, teclado y lector de pantalla queda pendiente. Las comprobaciones DOM no acreditan WCAG. No se incorporaron `referencia/`, `reports/`, `cookies.txt`, configuraciones privadas ni `test_postgres.py` como evidencia.
