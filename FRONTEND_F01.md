# ContinuitY · PBI-F01 — Pantalla de acceso

## Alcance
Pantalla visual responsive y accesible de login. No envía credenciales ni autentica todavía: el registro se implementará en PBI-F02 y el login web en PBI-F03. Los seis endpoints existentes se conservan.

## Ejecución
Desde la raíz del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest -v
CONTINUITY_ENV=development uvicorn app.main:app --reload
```

Abrir http://127.0.0.1:8000/login (para la API: /docs).

## Decisiones
- Archivo HTML en `app/templates/login.html`.
- Estilos en `app/static/css/{base,login}.css`.
- JavaScript de interacción visual en `app/static/js/login.js`.
- No se emplean scripts o estilos inline ni frameworks visuales.
- `lang=es`, UTF-8, un h1, labels explícitos, contraste y foco visible; `noindex` para el login.
- Sin cambios de negocio, autenticación ni almacenamiento.

## Verificación visual recomendada
Inspeccionar en escritorio y móvil, navegación solo por teclado, zoom al 200 %, foco y lectura con lector de pantalla. Estas comprobaciones manuales no equivalen a certificación WCAG.
