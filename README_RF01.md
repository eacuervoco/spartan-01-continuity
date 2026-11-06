# ContinuitY RF01 — Frontend integrado (PBI-F02/F03/F04)

Continúa sobre el backend PBI-06 y frontend F01. **No incluye base de datos**: el almacenamiento sigue en memoria.

## Arranque
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest -v
CONTINUITY_ENV=development uvicorn app.main:app --reload
```

Abrir `http://127.0.0.1:8000/login` y navegar hacia `/register`.

## Recorrido de verificación
1. Crear usuario desde `/register`; debe aparecer confirmación y enlace al login.
2. Iniciar sesión en `/login`; redirige a `/access`.
3. Verificar el destino lógico de incorporación empresarial (no hay empresas habilitadas en esta fase).
4. Cerrar sesión desde `/access` (consulta `/auth/csrf` y POST `/auth/logout`).
5. Acceder a `/access` otra vez sin sesión: redirige al login.
6. Comprobar navegador móvil, zoom 200 %, tabulación y mensajes de validación.

## Limitaciones
- Cookies con `Secure` en producción HTTPS; usar `CONTINUITY_ENV=development` **solo en localhost**.
- Los endpoints `/auth` y el almacenamiento en memoria son los mismos del backend validado.
- El servidor devuelve `PANEL` únicamente con membresía real autorizada; no se implementa panel ni incorporación empresarial.
- Se han incluido pruebas de integración HTTP y de estructura HTML, pero se requiere auditoría manual real WCAG y revisión de navegador.
- El backend exige verificación de origen y token CSRF en logout. Formularios de login y registro emplean la verificación de origen existente, y el alcance de cookie se mantiene en `/auth`.

## Evidencias de prueba
- pytest: 66 pruebas aprobadas (58 previas + 8 nuevas).
- `node --check`: cuatro archivos JavaScript sin errores de sintaxis.
- Prueba automatizada en navegador real: pendiente; Chromium no está instalado en el entorno de construcción.
- Auditoría WCAG y responsive manual: pendiente de validación en SpartanLab.
