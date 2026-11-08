# Índice verificable de pruebas existentes

Base: main, 1f858c0. Nombres y líneas extraídos de las pruebas originales. No acredita su ejecución; consultar revision.md.

## tests/test_access.py

- `tests/test_access.py::test_me_requiere_sesion` (línea 25).
- `tests/test_access.py::test_me_muestra_contexto_minimo_sin_secretos` (línea 29).
- `tests/test_access.py::test_me_despues_de_logout_es_401` (línea 41).
- `tests/test_access.py::test_me_usuario_eliminado_rechazado` (línea 48).
- `tests/test_access.py::test_servicio_permite_panel_solo_con_autorizacion_explicita` (línea 56).
- `tests/test_access.py::test_autorizacion_ambigua_no_da_panel` (línea 68).
- `tests/test_access.py::test_error_membership_falla_cerrado` (línea 78).
- `tests/test_access.py::test_usuario_ausente_servicio` (línea 88).

## tests/test_bd03_integracion.py


## tests/test_bd04_integracion.py


## tests/test_companies_api.py

- `tests/test_companies_api.py::test_registro_y_consulta_publica_con_normalizacion` (línea 38).
- `tests/test_companies_api.py::test_limites_normalizados_y_opcionales_omitidos` (línea 57).
- `tests/test_companies_api.py::test_opcionales_nulos_o_vacios` (línea 67).
- `tests/test_companies_api.py::test_entrada_invalida_no_guarda` (línea 79).
- `tests/test_companies_api.py::test_sin_sesion_es_401` (línea 87).
- `tests/test_companies_api.py::test_sesion_no_vigente_rechazada` (línea 93).
- `tests/test_companies_api.py::test_csrf_requerido` (línea 109).
- `tests/test_companies_api.py::test_origen_rechazado` (línea 116).
- `tests/test_companies_api.py::test_duplicado_409_conserva_original` (línea 123).
- `tests/test_companies_api.py::test_aislamiento_y_csrf_ligado_a_sesion` (línea 131).
- `tests/test_companies_api.py::test_fallos_internos_son_500_sin_detalles` (línea 144).
- `tests/test_companies_api.py::test_colision_de_guardado_devuelve_409` (línea 163).
- `tests/test_companies_api.py::test_modo_postgres_compone_sin_conectar` (línea 173).

## tests/test_company_repositories.py

- `tests/test_company_repositories.py::test_traduce_solo_unique_del_usuario` (línea 27).
- `tests/test_company_repositories.py::test_consulta_recupera_empresa_y_ausencia` (línea 49).
- `tests/test_company_repositories.py::test_memory_creacion_simultanea_no_sobrescribe` (línea 62).

## tests/test_company_service.py

- `tests/test_company_service.py::test_registro_genera_uuid_fecha_utc_y_asocia_usuario` (línea 32).
- `tests/test_company_service.py::test_normaliza_extremos_y_conserva_espacios_internos` (línea 46).
- `tests/test_company_service.py::test_opcionales_vacios_se_normalizan_a_none` (línea 57).
- `tests/test_company_service.py::test_limites_inclusivos_se_validan_despues_de_normalizar` (línea 62).
- `tests/test_company_service.py::test_datos_invalidos_no_guardan_empresa` (línea 78).
- `tests/test_company_service.py::test_entidad_impide_identificadores_y_fecha_invalidos` (línea 90).
- `tests/test_company_service.py::test_entidad_normaliza_fecha_a_utc_y_es_inmutable` (línea 98).
- `tests/test_company_service.py::test_consulta_sin_empresa_devuelve_none` (línea 108).
- `tests/test_company_service.py::test_segundo_registro_no_sobrescribe_empresa` (línea 113).
- `tests/test_company_service.py::test_usuarios_aislados_pueden_compartir_nit` (línea 123).
- `tests/test_company_service.py::test_colision_al_crear_se_traduce_a_duplicado` (línea 134).
- `tests/test_company_service.py::test_errores_de_repositorio_no_se_confunden_con_duplicidad` (línea 150).

## tests/test_foundation.py

- `tests/test_foundation.py::test_usuario_valido_activo_cliente` (línea 17).
- `tests/test_foundation.py::test_no_existe_no_es_estado_persistible` (línea 24).
- `tests/test_foundation.py::test_cuenta_inexistente_y_activa` (línea 29).
- `tests/test_foundation.py::test_registro_dual_sin_parcialidad_si_ids_no_coinciden` (línea 38).
- `tests/test_foundation.py::test_correo_duplicado_no_sobrescribe_credencial` (línea 47).
- `tests/test_foundation.py::test_sesion_vigente_y_expirada` (línea 58).
- `tests/test_foundation.py::test_invalidacion_impide_reutilizacion` (línea 68).
- `tests/test_foundation.py::test_fechas_sin_zona_horaria_se_rechazan` (línea 76).
- `tests/test_foundation.py::test_contratos_y_autorizacion_cerrada` (línea 81).

## tests/test_frontend_f01.py

- `tests/test_frontend_f01.py::test_pagina_login_se_sirve_con_utf8_y_meta_basicas` (línea 19).
- `tests/test_frontend_f01.py::test_semantica_un_solo_h1_y_campos_etiquetados` (línea 29).
- `tests/test_frontend_f01.py::test_codigo_y_estilos_externos` (línea 41).
- `tests/test_frontend_f01.py::test_api_anterior_continua_disponible` (línea 50).

## tests/test_frontend_integrated.py

- `tests/test_frontend_integrated.py::test_vistas_y_metadatos` (línea 11).
- `tests/test_frontend_integrated.py::test_recursos_estaticos_por_separado` (línea 25).
- `tests/test_frontend_integrated.py::test_registro_login_contexto_y_logout` (línea 34).
- `tests/test_frontend_integrated.py::test_sin_autenticacion_no_hay_contexto` (línea 54).
- `tests/test_frontend_integrated.py::test_login_mensaje_generico` (línea 60).
- `tests/test_frontend_integrated.py::test_registro_rechaza_contrasenas_distintas` (línea 67).
- `tests/test_frontend_integrated.py::test_no_se_exponen_secretos_en_me` (línea 73).
- `tests/test_frontend_integrated.py::test_csrf_incorrecto_no_cierra_sesion` (línea 82).

## tests/test_frontend_rf02.py

- `tests/test_frontend_rf02.py::test_empresa_semantica_oculta_y_campos_accesibles` (línea 25).
- `tests/test_frontend_rf02.py::test_access_y_recursos_empresa_se_sirven` (línea 56).
- `tests/test_frontend_rf02.py::test_flujo_http_access_empresa_y_nueva_sesion` (línea 64).
- `tests/test_frontend_rf02.py::test_javascript_rf02_con_dom_simulado` (línea 88).

## tests/test_login.py

- `tests/test_login.py::test_login_correcto_crea_sesion_y_cookie` (línea 21).
- `tests/test_login.py::test_login_invalido_mensaje_generico_y_sin_cookie` (línea 41).
- `tests/test_login.py::test_limitador_ip_y_correo` (línea 48).
- `tests/test_login.py::test_sesiones_distintas_por_login` (línea 57).
- `tests/test_login.py::test_password_no_se_expone_en_validacion` (línea 66).
- `tests/test_login.py::test_no_se_guarda_sesion_si_falla_validacion` (línea 71).
- `tests/test_login.py::test_credencial_inexistente_no_autentica` (línea 80).

## tests/test_postgres_companies.py

- `tests/test_postgres_companies.py::test_pg_persistencia_tras_reconexion` (línea 77).
- `tests/test_postgres_companies.py::test_pg_opcionales_y_aislamiento` (línea 83).
- `tests/test_postgres_companies.py::test_pg_fk_rechaza_usuario_inexistente` (línea 91).
- `tests/test_postgres_companies.py::test_pg_unique_usuario_sin_sobrescritura` (línea 99).
- `tests/test_postgres_companies.py::test_pg_colision_concurrente` (línea 108).
- `tests/test_postgres_companies.py::test_pg_fallo_de_insercion_no_deja_registro` (línea 128).
- `tests/test_postgres_companies.py::test_pg_permisos_minimos` (línea 138).
- `tests/test_postgres_companies.py::test_pg_api_nueva_aplicacion_y_nueva_sesion` (línea 148).

## tests/test_quality.py

- `tests/test_quality.py::test_auditoria_cubre_registro_login_y_logout_sin_secretos` (línea 17).
- `tests/test_quality.py::test_auditoria_validacion_rechazada_sin_datos_sensibles` (línea 39).
- `tests/test_quality.py::test_logout_sin_csrf_es_rechazado_y_auditado` (línea 49).
- `tests/test_quality.py::test_logout_no_permite_reutilizar_cookie_anterior` (línea 59).

## tests/test_registration.py

- `tests/test_registration.py::test_registro_valido_sin_inicio_de_sesion` (línea 25).
- `tests/test_registration.py::test_correo_duplicado_case_insensitive` (línea 42).
- `tests/test_registration.py::test_datos_invalidos` (línea 53).
- `tests/test_registration.py::test_campos_extra_rechazados` (línea 58).
- `tests/test_registration.py::test_fallo_del_hash_no_crea_usuario` (línea 62).
- `tests/test_registration.py::test_fallo_repositorio_no_expone_excepcion` (línea 75).
- `tests/test_registration.py::test_colision_en_guardado_transformada_a_conflicto` (línea 86).

## tests/test_sessions.py

- `tests/test_sessions.py::test_ruta_protegida_sin_cookie` (línea 28).
- `tests/test_sessions.py::test_sesion_vigente` (línea 33).
- `tests/test_sessions.py::test_actualizar_actividad_sin_extender_limite_absoluto` (línea 40).
- `tests/test_sessions.py::test_inactividad_de_30_minutos` (línea 50).
- `tests/test_sessions.py::test_limite_absoluto_ocho_horas` (línea 60).
- `tests/test_sessions.py::test_logout_requiere_csrf` (línea 70).
- `tests/test_sessions.py::test_logout_invalida_token_y_cookie` (línea 77).
- `tests/test_sessions.py::test_csrf_es_especifico_para_cada_sesion` (línea 90).
- `tests/test_sessions.py::test_origen_cruzado_rechazado` (línea 104).
- `tests/test_sessions.py::test_logout_origen_cruzado_rechazado` (línea 111).
- `tests/test_sessions.py::test_sesion_ausente_no_se_reactiva` (línea 118).
