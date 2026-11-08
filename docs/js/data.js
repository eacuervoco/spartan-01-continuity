/* Fichas de síntesis académica. No sustituyen la aprobación de requisitos. */
"use strict";
(() => {
  const criterion = (id, scenario, condition, action, expected, evidence, status = "Cumple · pruebas automatizadas en memoria") => ({id, scenario, condition, action, expected, evidence, status});
  const rf01 = {
    id: "RF01", name: "Registro, autenticación y gestión de sesiones", implemented: true,
    objective: "Permitir el acceso inicial a ContinuitY mediante una cuenta y una sesión vigente.",
    description: "Registro con correo normalizado, inicio de sesión, consulta de contexto, expiración y cierre de sesión. Síntesis del código y de la documentación RF01.",
    actor: "Usuario de ContinuitY", inputs: "Nombre, correo, contraseña y confirmación en el sistema real; únicamente datos de demostración en el portal.",
    outputs: "Cuenta creada, acceso autorizado o mensaje de validación; contexto de sesión.",
    preconditions: "Para registrarse: correo no registrado. Para acceder: cuenta existente y credenciales válidas. Para consultar contexto: sesión vigente.",
    rules: ["Cuenta: ACTIVA; NO EXISTE es resultado de consulta y no un estado persistido.", "Sesión: VIGENTE o EXPIRADA. Inactividad de 30 minutos y límite absoluto de 8 horas en el backend.", "Correo válido, normalizado y único; nombre obligatorio (máximo 120 por API); contraseña de 12 a 1024 caracteres por API y confirmación coincidente. Registro no inicia sesión automáticamente.", "El backend protege credenciales con Argon2id, verifica origen y requiere CSRF para logout. El portal no reproduce seguridad real."],
    story: "Como usuario de ContinuitY, quiero crear una cuenta e iniciar y cerrar sesión, para acceder de forma controlada a mi contexto empresarial.",
    source: "evidence/sources.md#rf01", screen: "Registro / Inicio de sesión / Mi acceso (simulación)",
    postconditions: "Registro: cuenta ACTIVA y credencial creadas sin iniciar sesión. Login: sesión nueva. Logout o expiración: acceso posterior denegado.",
    criteria: [
      criterion("RF01-CA01", "Registro válido", "Correo no registrado", "POST /auth/register con nombre, correo y clave válida", "201; ACTIVA, CLIENTE; correo normalizado; sin cookie ni contraseña en respuesta", "tests/test_registration.py::test_registro_valido_sin_inicio_de_sesion"),
      criterion("RF01-CA02", "Registro inválido", "Cuenta inexistente", "Enviar nombre vacío, correo inválido, clave <12 o confirmación distinta", "422; sin crear usuario", "tests/test_registration.py::test_datos_invalidos"),
      criterion("RF01-CA03", "Correo duplicado", "Correo ya registrado", "Registrar el mismo correo con otras mayúsculas", "409; sin segunda cuenta", "tests/test_registration.py::test_correo_duplicado_case_insensitive"),
      criterion("RF01-CA04", "Inicio de sesión", "Cuenta con credencial", "POST /auth/login con clave correcta / incorrecta o cuenta ausente", "200 y cookie / 401 genérico sin cookie", "tests/test_login.py::test_login_correcto_crea_sesion_y_cookie; tests/test_login.py::test_login_invalido_mensaje_generico_y_sin_cookie"),
      criterion("RF01-CA05", "Consulta y acceso restringido", "Sesión vigente / cookie ausente", "GET /auth/session y /auth/me", "Contexto propio con sesión; 401 sin sesión", "tests/test_sessions.py::test_sesion_vigente; tests/test_sessions.py::test_ruta_protegida_sin_cookie; tests/test_access.py"),
      criterion("RF01-CA06", "Límites temporales", "Sesión creada", "Autenticar a los 30 min sin actividad o a las 8 h absolutas", "EXPIRADA; token invalidado; actividad no extiende duración absoluta", "tests/test_sessions.py::test_inactividad_de_30_minutos; tests/test_sessions.py::test_limite_absoluto_ocho_horas; tests/test_sessions.py::test_actualizar_actividad_sin_extender_limite_absoluto"),
      criterion("RF01-CA07", "Cierre y reutilización", "Sesión vigente y CSRF válido", "POST /auth/logout; reutilizar cookie anterior", "200 y eliminación cookie; posterior 401", "tests/test_sessions.py::test_logout_invalida_token_y_cookie; tests/test_quality.py::test_logout_no_permite_reutilizar_cookie_anterior"),
      criterion("RF01-CA08", "Origen y CSRF", "Sesión vigente para logout", "Enviar origen cruzado a registro/login/logout o logout sin CSRF", "403; petición rechazada", "tests/test_sessions.py::test_origen_cruzado_rechazado; tests/test_sessions.py::test_logout_requiere_csrf; tests/test_sessions.py::test_logout_origen_cruzado_rechazado"),
      criterion("RF01-CA09", "Intentos de login", "Cinco fallos dentro de 15 minutos", "Intentar un nuevo login por la misma IP o correo", "429; Retry-After 900", "tests/test_login.py::test_limitador_ip_y_correo"),
      criterion("RF01-CA10", "Persistencia y revocación PostgreSQL", "BD de pruebas con migraciones", "Reabrir repositorios; revocar e intentar guardar sesión anterior", "Cuenta persistida; sesión revocada no se reactiva", "tests/test_bd03_integracion.py; tests/test_bd04_integracion.py", "Pendiente: integración PostgreSQL no ejecutada")
    ]
  };
  const rf02 = {
    id: "RF02", name: "Registro y asociación de empresa", implemented: true,
    objective: "Registrar una empresa por usuario y permitir su consulta posterior.",
    description: "RF02 está integrado en main. La API real utiliza POST /auth/companies y GET /auth/companies/me; difiere de las rutas sugeridas en la especificación.",
    actor: "Usuario registrado con sesión vigente", inputs: "Nombre de empresa, ciudad y, opcionalmente, NIT y sector.", outputs: "Empresa asociada al usuario autenticado o error comprensible.",
    preconditions: "RF01 disponible; sesión vigente; usuario sin empresa para crear un registro.",
    rules: ["Una sola empresa por usuario en el MVP; UNIQUE(usuario_id) también protege concurrencia.", "Nombre obligatorio, máximo 150 caracteres; ciudad obligatoria, máximo 100. Se eliminan espacios exteriores.", "NIT opcional (máximo 20), sector opcional (máximo 100). No se exige NIT único ni se consulta DIAN.", "El propietario proviene de la sesión, nunca del formulario. Consulta limitada a la empresa propia.", "Sin sesión: 401; entrada inválida: 422; duplicado: 409; fallo interno: 500 controlado. POST exige origen y CSRF.", "No incluye edición, eliminación, invitaciones ni empresas multiusuario."],
    story: "Como usuario autenticado, quiero registrar y consultar mi empresa, para asociar a ella futuros procesos de consultoría tecnológica.",
    source: "evidence/sources.md#rf02", screen: "Mi empresa: formulario y consulta (simulación)",
    postconditions: "Empresa creada con UUID y fecha UTC, vinculada al usuario de sesión; consulta propia disponible. Un error no sobrescribe el registro anterior.",
    criteria: [
      criterion("RF02-CA01", "Registro y consulta", "Sesión vigente; sin empresa", "POST /auth/companies y GET /auth/companies/me", "201 y 200 con los mismos datos normalizados, UUID y fecha UTC", "tests/test_companies_api.py::test_registro_y_consulta_publica_con_normalizacion"),
      criterion("RF02-CA02", "Opcionales y límites", "Sesión vigente; sin empresa", "Enviar nombre de 150, ciudad de 100; omitir NIT y sector o enviarlos vacíos", "201; opcionales nulos", "tests/test_companies_api.py::test_limites_normalizados_y_opcionales_omitidos; tests/test_companies_api.py::test_opcionales_nulos_o_vacios; tests/test_company_service.py::test_limites_inclusivos_se_validan_despues_de_normalizar"),
      criterion("RF02-CA03", "Persistencia PostgreSQL", "BD de pruebas migrada", "Registrar; reconectar o iniciar nueva aplicación y sesión", "Consultar la misma empresa", "tests/test_postgres_companies.py::test_pg_persistencia_tras_reconexion; tests/test_postgres_companies.py::test_pg_api_nueva_aplicacion_y_nueva_sesion", "Pendiente: integración PostgreSQL no ejecutada"),
      criterion("RF02-CA04", "Propietario confiable", "Sesión vigente", "Enviar usuario_id como campo adicional", "422; no guarda; propietario se toma de sesión", "tests/test_companies_api.py::test_entrada_invalida_no_guarda"),
      criterion("RF02-CA05", "Aislamiento", "Dos usuarios autenticados", "Consultar y registrar con la segunda sesión", "No ve empresa de la primera; puede compartir NIT", "tests/test_companies_api.py::test_aislamiento_y_csrf_ligado_a_sesion; tests/test_company_service.py::test_usuarios_aislados_pueden_compartir_nit"),
      criterion("RF02-CA06", "Duplicidad", "Usuario con empresa", "Registrar otra o simular colisión de guardado", "409; conserva empresa original", "tests/test_companies_api.py::test_duplicado_409_conserva_original; tests/test_companies_api.py::test_colision_de_guardado_devuelve_409"),
      criterion("RF02-CA07", "Sin autorización", "Sesión ausente, inactiva, expirada o revocada", "POST o GET de empresa", "401", "tests/test_companies_api.py::test_sin_sesion_es_401; tests/test_companies_api.py::test_sesion_no_vigente_rechazada"),
      criterion("RF02-CA08", "Entrada inválida", "Sesión vigente", "Omitir obligatorios, exceder límites 150/100/20/100 o enviar tipos inválidos", "422; consulta posterior 404 si no había empresa", "tests/test_companies_api.py::test_entrada_invalida_no_guarda; tests/test_company_service.py::test_datos_invalidos_no_guardan_empresa"),
      criterion("RF02-CA09", "Protección y errores", "Sesión vigente", "POST sin CSRF o con origen cruzado; provocar fallo de repositorio", "403 en protección; 500 genérico ante fallo interno", "tests/test_companies_api.py::test_csrf_requerido; tests/test_companies_api.py::test_origen_rechazado; tests/test_companies_api.py::test_fallos_internos_son_500_sin_detalles"),
      criterion("RF02-CA10", "Interfaz de empresa", "Mi acceso con sesión", "Abrir Mi empresa, registrar y consultar", "Formulario etiquetado y consulta de solo lectura; visual/móvil pendientes", "tests/test_frontend_rf02.py; tests/frontend_rf02.test.cjs", "Parcial: automatización; revisión visual pendiente")
    ]
  };
  const statuses = ["Sin evaluar", "Cumple", "No cumple", "Requiere ajustes"];
  const dimensions = ["Claridad", "Navegación", "Consistencia visual", "Validaciones", "Cobertura de criterios"];
  const controls = [
    ["Argon2id", "Exposición de contraseñas", "time_cost=3, memory_cost=65536 KiB, parallelism=4; hash con sal aleatoria", "app/infrastructure/security.py; tests/test_registration.py"],
    ["Correo normalizado y único", "Cuentas duplicadas por variación de correo", "strip + casefold en servicio; UNIQUE y CHECK lower/btrim en SQL", "app/core/registration.py; database/001_schema.sql; tests/test_registration.py"],
    ["Token opaco y digest", "Predicción de sesión y exposición de tokens persistidos", "token_urlsafe(32); PostgreSQL guarda SHA-256 del token; memoria guarda token", "app/core/login.py; app/infrastructure/postgres_sessions.py; tests/test_bd04_integracion.py (no ejecutado)"],
    ["Cookie de sesión", "Lectura desde JavaScript y envío sin TLS", "HttpOnly, SameSite=lax, Path=/auth, Max-Age 8 h; Secure salvo development", "app/api/auth.py; app/main.py; tests/test_login.py"],
    ["Origen y CSRF", "Solicitudes desde otro sitio", "Registro/login verifican Origin y Sec-Fetch-Site; logout y POST empresa añaden HMAC ligado a sesión, comparación constante. GET privados exigen sesión.", "app/api/origin.py; app/api/session.py; app/api/companies.py; tests/test_sessions.py; tests/test_companies_api.py"],
    ["Intentos de login", "Fuerza bruta", "Cinco fallos por IP y correo en 15 min; siguiente intento 429. Limitador solo por proceso.", "app/infrastructure/rate_limit.py; tests/test_login.py"],
    ["Expiración e invalidación", "Reutilización de sesiones", "30 min de inactividad, 8 h absolutas; logout invalida. PostgreSQL conserva revocada_en y evita resurrección por UPSERT.", "app/core/session_service.py; app/infrastructure/postgres_sessions.py; tests/test_sessions.py; tests/test_bd04_integracion.py (no ejecutado)"],
    ["SQL parametrizado", "Inyección SQL mediante datos", "execute con marcadores %s y parámetros separados en los tres repositorios", "app/infrastructure/postgres_users.py; postgres_sessions.py; postgres_companies.py; integración PostgreSQL pendiente"],
    ["Acceso restrictivo", "Acceso privado sin sesión o a otra empresa", "Dependencia usuario_autenticado: 401; empresa filtrada por usuario de sesión; campos extra prohibidos; sin autorización de membresía por defecto", "app/api/session.py; app/api/companies.py; app/core/access_service.py; tests/test_access.py; tests/test_companies_api.py"]
  ];
  window.PortalData = Object.freeze({requirements: [rf01, rf02], statuses, dimensions, controls});
})();
