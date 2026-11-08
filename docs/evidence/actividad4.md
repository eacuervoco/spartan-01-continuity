# Actividad 4 - Diseño del prototipo

Revisión local del 8 de noviembre de 2026. Estado: **APROBABLE** para el prototipo estático del alcance solicitado. Sin commit, push, merge ni publicación. No se verificó el sitio remoto.

## Cambio y fuentes

Se actualizaron la presentación y E en RF01/RF02: inicio de sesión, registro, Mi acceso y Mi empresa (formulario y ficha de solo lectura). Marca, ilustración CSS de oportunidades, paneles blanco/verde, botones naranja y jerarquía se adaptaron de `app/templates/login.html`, `register.html`, `access.html` y `app/static/css/base.css`, `login.css`, `company.css`. Se contrastaron los scripts `login.js`, `register.js` y `access.js`; su comunicación con el backend se sustituye por el modelo ficticio en memoria ya existente del portal.

No se encontraron archivos de imagen CY1, CY2, CY3 ni CY4 en el workspace. No se usaron ni se atribuyó inspección a esas capturas. Las capturas nuevas de validación tienen nombres de vista y ancho; no representan CY1–CY4.

A, B, C y F conservan su contenido. D solo corrige el estado de revisión visual y enlaza este registro; la evidencia histórica permanece disponible en [revisión anterior](revision.md) y [pytest anterior](pytest.txt). Se añadieron accesos A–F y anclas por ficha. Una corrección del ancho mínimo del grid evita que la matriz académica ensanche la página en móvil. El portal conserva un H1 por vista; la demostración usa H3.

## Flujo final

Crear cuenta → inicio de sesión → Mi acceso → Mi empresa → registrar empresa → ficha de solo lectura → cerrar sesión → iniciar sesión nuevamente → Mi empresa / consultar empresa. Volver a Mi acceso permite regresar desde el formulario o la ficha. Los datos ficticios sobreviven al cierre de sesión y a la navegación entre RF01/RF02; recargar la pestaña los elimina.

## Criterios cubiertos

- Nombre no vacío tras recortar espacios y máximo 120 caracteres; correo válido ficticio (dominios example.test/com/org), máximo 254; contraseña entre 12 y 1024 caracteres; confirmación coincidente.
- Correos duplicados normalizados, credenciales correctas e incorrectas, ocultar/mostrar contraseña y mensajes de error/confirmación.
- Vistas privadas condicionadas a sesión simulada, cierre de sesión y consulta posterior sin perder la empresa en memoria.
- Nombre y ciudad obligatorios; NIT y sector opcionales; límites respectivos 150/100/20/100, incluidos máximos válidos y rechazos al excederlos.
- Una empresa por usuario, ficha de solo lectura y separación entre usuarios. El formulario desaparece al registrar; consultar devuelve la empresa existente.
- Datos de usuario insertados con `textContent`. Cadenas con etiquetas se muestran literalmente. Sin solicitudes API, almacenamiento de contraseñas en localStorage/sessionStorage ni recursos remotos. Las evaluaciones de F conservan su almacenamiento local independiente.
- Etiquetas asociadas, teclado, mostrar/ocultar accesible, foco al cambiar de vista y mensajes `role=status` con `aria-live=polite`.

No quedan criterios funcionales solicitados pendientes dentro del simulador. Esto no acredita autenticación segura, CSRF, cookies, expiración real ni persistencia PostgreSQL.

## Validación ejecutada

| Comprobación | Aprobadas | Fallidas | Omitidas | Alcance |
| --- | ---: | ---: | ---: | --- |
| `.venv/bin/python -m pytest -ra` (límite 180 s) | 131 | 0 | 8 | 139 recolectadas, 36.85 s; backend existente |
| `node tests/frontend_rf02.test.cjs` | 19 | 0 | 0 | Frontend real con DOM/API simulados |
| `python3 docs/checks/validate.py` | 5 | 0 | 0 | Portal con DOM simulado y 18 instantáneas HTML |
| `python docs/checks/browser-activity4.py` | 5 | 0 | 0 | Chromium real con archivos locales bajo prefijo Pages |

Las entradas `validate.py` y `portal.test.cjs` delegan al conjunto vigente RF01/RF02. Sus expectativas históricas de doce fichas y siete apartados se sustituyen por las seis secciones vigentes; no se cuentan dos veces como pruebas nuevas. Se ampliaron las comprobaciones del simulador, manteniendo evaluación, fuentes y navegación.

Pytest reportó una advertencia `StarletteDeprecationWarning` por httpx/TestClient. Las ocho omisiones corresponden a `tests/test_postgres_companies.py`: requieren aprobación del destino PostgreSQL, migraciones y escrituras. No se ejecutaron los scripts manuales de integración BD03/BD04 ni migraciones. La primera ejecución de pytest restringida quedó sin resultado al iniciar TestClient; el resultado de la tabla proviene de la repetición fuera del sandbox. Chromium también necesitó ejecución fuera del sandbox, que bloqueaba su arranque. No se instalaron dependencias.

El navegador verificó errores y casos positivos, empresa del usuario correcto, persistencia tras nuevo login y eliminación al recargar; inyección de texto sin crear nodos; teclado, foco y labels; evaluación F y navegación de ambas fichas. Se probaron login, registro, acceso, formulario de empresa y ficha en **320, 375, 768, 1024 y 1440 px**, sin desbordamiento horizontal del documento y con controles dentro del viewport. Recursos servidos bajo `/spartan-01-continuity/`, sin recursos faltantes ni errores JavaScript. Las tablas conservan desplazamiento interno horizontal.

`git diff --check`: sin errores. Sin diferencias en `app/`, `database/`, `tests/`, `scripts/` ni `pyproject.toml`.

## Evidencia y reproducción en navegador

Desde la raíz del repositorio:

```bash
python3 -m http.server 8080 --directory docs
```

Abrir `http://localhost:8080/#requisitos/RF01/E`. Crear una cuenta ficticia (por ejemplo, `consultor@example.test`, contraseña inventada `DemoContinuitY12!`), iniciar sesión y completar el flujo anterior. Probar nombre vacío/espacios, correo inválido/duplicado, contraseña corta, confirmación distinta, login incorrecto y empresa sin nombre/ciudad. Iniciar otra cuenta para comprobar que no ve la empresa anterior. Repetir desde RF02 y revisar F. Recargar para comprobar que desaparecen las cuentas ficticias.

Comprobación estándar sin dependencias adicionales:

```bash
python3 docs/checks/validate.py
node tests/frontend_rf02.test.cjs
```

Pruebas reales de navegador, si Playwright y Chromium ya están disponibles:

```bash
python docs/checks/browser-activity4.py
```

En este workspace se reutilizó el entorno previamente disponible (sin agregar dependencias al proyecto):

```bash
PLAYWRIGHT_BROWSERS_PATH=/tmp/continuity-rf02-browsers LD_LIBRARY_PATH=/tmp/continuity-rf02-browser/libs/usr/lib/x86_64-linux-gnu /tmp/continuity-rf02-browser/bin/python docs/checks/browser-activity4.py
```

Ese comando genera diez capturas nuevas en `/tmp/continuity-activity4/`: `login`, `register`, `access`, `company-form` y `company-details`, cada una a 375 y 1440 px. No se incluyen como capturas originales ni se publican automáticamente.

Se inspeccionaron capturas de escritorio y móvil y se comprobaron las dimensiones mediante Chromium. No se realizó auditoría WCAG completa, lector de pantalla, Firefox/Safari, revisión manual en dispositivo físico ni comprobación del despliegue público. La validación PostgreSQL sigue fuera del simulador. La aceptación docente en F conserva su estado independiente.

## Archivos de esta actualización

- `docs/index.html`: presentación y carga de recursos relativos.
- `docs/js/app.js`: integración E y navegación de apartados.
- `docs/js/prototype.js`: interfaz de cuatro vistas, reutilizada en ambas fichas.
- `docs/css/prototype.css`: estilos originales adaptados y aislados del portal.
- `docs/css/styles.css`: ancho del grid académico en móvil.
- `docs/checks/rf01-rf02.test.cjs`: pruebas específicas del portal vigente ampliadas.
- `docs/checks/portal.test.cjs`: entrada al conjunto vigente, sin duplicación.
- `docs/checks/validate-rf01-rf02.py`: aclaración del alcance DOM frente al navegador.
- `docs/checks/validate.py`: entrada al validador vigente.
- `docs/checks/browser-activity4.py`: cinco pruebas de navegador y capturas reproducibles.
- `docs/evidence/actividad4.md`: este registro, separado de la evidencia histórica.
