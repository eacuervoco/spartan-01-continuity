# Revisión del portal académico · RF01 y RF02

Fecha: 7 de noviembre de 2026, America/Bogota. Base auditada: rama local `main`, commit `1f858c0` (merge de RF02). No se cambió de rama ni se hicieron commits, fusiones o push. La configuración y disponibilidad remota de GitHub Pages no se verificaron ni modificaron.

## Revisión realizada

Se contrastaron servicios, entidades, API, clases de persistencia, migraciones SQL, frontend original, pruebas y documentación del portal. Código, SQL y pruebas de main prevalecen sobre especificaciones históricas incompatibles. Las [fuentes](sources.md), los [extractos de implementación](implementation.md), el [índice de pruebas](test-index.md) y sus [extractos](test-excerpts.md) permiten revisar los escenarios sin acceder a configuraciones o datos privados.

El estado inicial ya contenía README modificado y archivos no versionados del portal, además de `referencia/`, `reports/` y `test_postgres.py`. Se trabajó sobre ese portal conservando su marca y estilos. Los archivos locales ajenos a la tarea no se modificaron ni se incorporan como evidencia funcional.

Se retiraron las fichas adicionales, el séptimo apartado de trazabilidad y el plan académico de sprints sin ejecución acreditada. La trazabilidad se integra en las historias, matrices y fuentes. La navegación evaluable tiene una introducción y únicamente RF01/RF02; cada ficha tiene seis apartados A–F. El objetivo de diagnóstico más interacción con IA queda expresamente planificado, sin simulación ni resultados inventados.

D incorpora las cuatro tablas reales, PK/FK, cardinalidades, unicidad, integridad, transacciones, SVG local y Mermaid. RF01 incluye una matriz de controles de seguridad con sus límites. E ofrece registro, login, validaciones, consulta/cierre de sesión y empresa propia simulados. Solo admite claves públicas de práctica mediante campos de solo lectura y controles para provocar errores; la demo no persiste claves ni realiza solicitudes de red. F separa evaluación docente de prueba técnica: dimensiones, criterios, observaciones y conclusión inician Sin evaluar; se guardan localmente, se descargan como JSON o se imprimen.

## Entorno y regresión existente

Linux; Python 3.12.3 de `.venv`, pytest 9.2.0, AnyIO 4.15.1; Node v26.13.0. No se instalaron dependencias ni se ejecutaron migraciones. No se habilitó PostgreSQL.

El primer intento restringido de `.venv/bin/python -m pytest -ra` llegó a recolectar 139 casos y quedó sin resultado concluyente al iniciar TestClient. Se repitió fuera del sandbox mediante la aprobación de ejecución del entorno:

```bash
timeout 180s .venv/bin/python -m pytest -ra
```

Resultado real: **131 passed, 8 skipped, 1 warning in 46.76s**. [Salida conservada](pytest.txt). Las pruebas API ejecutadas usan almacenamiento en memoria; las pruebas de repositorios con dobles no validan una instancia PostgreSQL.

Advertencia conservada: `StarletteDeprecationWarning`, por uso de `httpx` con `starlette.testclient`; recomienda `httpx2`. No se cambiaron dependencias para eliminarla.

Las ocho omisiones son de `tests/test_postgres_companies.py`, por destino, migración y escrituras PostgreSQL pendientes de habilitación explícita:

- `test_pg_persistencia_tras_reconexion`.
- `test_pg_opcionales_y_aislamiento`.
- `test_pg_fk_rechaza_usuario_inexistente`.
- `test_pg_unique_usuario_sin_sobrescritura`.
- `test_pg_colision_concurrente`.
- `test_pg_fallo_de_insercion_no_deja_registro`.
- `test_pg_permisos_minimos`.
- `test_pg_api_nueva_aplicacion_y_nueva_sesion`.

Además, `tests/test_bd03_integracion.py` y `test_bd04_integracion.py` son scripts manuales con `main()`: pytest importa los archivos pero no ejecuta sus comprobaciones PostgreSQL. **No se ejecutaron**; no cuentan entre las ocho omisiones de pytest ni como pruebas aprobadas de persistencia o revocación. Las matrices mantienen pendientes esas comprobaciones.

```bash
node tests/frontend_rf02.test.cjs
```

Resultado: **19 aprobadas, 0 fallidas**, con DOM y API simulados. [Salida conservada](frontend-rf02.txt). Verifican lógica del frontend existente; no renderizado real, PostgreSQL ni WCAG.

## Validación del portal vigente

```bash
python3 docs/checks/validate-rf01-rf02.py
```

Resultado: **4 pruebas aprobadas; 14 instantáneas comprobadas**. [Salida conservada](portal-rf01-rf02.txt). Usa Python estándar y Node, sin paquetes nuevos. Comprueba:

- Solo RF01/RF02; seis apartados A–F; un H1 por vista; rechazo de las rutas retiradas.
- Validaciones de registro, claves inválidas, confirmación distinta, sesión, apertura de Mi empresa, registro, duplicidad, aislamiento y consulta posterior.
- Evaluación inicialmente Sin evaluar, escape de texto guardado, persistencia local, descarga e impresión; manejo del almacenamiento denegado.
- Referencias de matrices a archivos y funciones existentes; criterios PostgreSQL sin Cumple automático.
- Recursos y rutas relativas, IDs sin duplicar, labels, anclas Markdown usadas por las vistas, SVG válido y sintaxis de todos los JavaScript del portal.

Las pruebas nuevas se añadieron en `docs/checks/rf01-rf02.test.cjs` y `validate-rf01-rf02.py`. Se conservaron intactas todas las pruebas existentes. El DOM simulado comprueba invocación de descarga/impresión, no el diálogo real ni el PDF producido por un navegador.

Las comprobaciones antiguas se ejecutaron y **fallan**:

```bash
node docs/checks/portal.test.cjs
python3 docs/checks/validate.py
```

El primero obtiene **1 aprobado y 3 fallidos**: espera doce fichas, siete apartados y rutas independientes de prototipo/evaluación retiradas. [Salida conservada](portal-historico.txt). El segundo falla al capturar `demo-content` desde la ruta retirada `#prototipo`. [Salida conservada](validacion-historica.txt). Se documenta la incompatibilidad y se ofrece un comando nuevo para el alcance solicitado; no se alteraron pruebas para fabricar aprobaciones.

`git diff --check` terminó sin errores. `git diff --exit-code main -- app database tests scripts pyproject.toml` terminó sin diferencias. Estos comandos no incluyen los archivos nuevos no versionados; el validador sí inspecciona los archivos del portal en disco.

## Pendientes y límites

- Integración PostgreSQL real RF01 y RF02, permisos y concurrencia; sin pruebas ni migraciones sobre destinos no habilitados.
- Comprobación visual en escritorio/móvil, teclado, lector de pantalla, zoom y contraste en navegador. No se encontró Chromium, Chrome ni Firefox disponible; no se instalaron navegadores. No se acredita WCAG.
- Confirmación docente: todos sus campos empiezan Sin evaluar en un navegador sin resultados guardados. La evaluación nunca se deriva de pytest.
- Verificar HTTPS, Secure y límites del despliegue backend; limitador compartido y revisión de permisos SQL, pendientes técnicos identificados, sin cambios de negocio en esta tarea.
- Publicar los cambios revisados y autorizados en `main` y confirmar GitHub Pages desde `/docs`. El portal está preparado para ese despliegue, pero esta revisión no acredita una publicación remota.

Para previsualizar: `python3 -m http.server 8080 --directory docs`. Para publicar: Settings → Pages → Deploy from a branch → `main` → `/docs`; usar la URL devuelta por GitHub después de integrar y publicar los cambios con autorización. No se creó infraestructura adicional ni se emplearon servicios externos para la demo o la evaluación.
