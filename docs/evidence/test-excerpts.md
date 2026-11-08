# Extractos verificables de pruebas

Base: main, 1f858c0. Funciones de prueba originales con líneas de origen; sin fixtures ni datos de ejecución. PASSWORD refiere a datos ficticios del test. No se publican valores de hashes, tokens ni cookies generados. Consultar revision.md para ejecución y omisiones.

## tests/test_access.py::test_me_requiere_sesion

```python
25: def test_me_requiere_sesion(cliente):
26:     assert cliente.get('/auth/me').status_code == 401
```

## tests/test_access.py::test_me_muestra_contexto_minimo_sin_secretos

```python
29: def test_me_muestra_contexto_minimo_sin_secretos(cliente):
30:     login(cliente)
31:     r = cliente.get('/auth/me')
32:     assert r.status_code == 200
33:     assert r.json()['email'] == 'cliente@ejemplo.com'
34:     assert r.json()['rol'] == 'CLIENTE'
35:     assert r.json()['estado'] == 'ACTIVA'
36:     assert r.json()['destino'] == 'INCORPORACION_EMPRESARIAL'
37:     assert set(r.json()) == {'id', 'nombre', 'email', 'estado', 'rol', 'destino'}
38:     assert PASSWORD not in r.text and 'hash' not in r.text and 'token' not in r.text
```

## tests/test_access.py::test_me_despues_de_logout_es_401

```python
41: def test_me_despues_de_logout_es_401(cliente):
42:     login(cliente)
43:     csrf = cliente.get('/auth/csrf').json()['csrf_token']
44:     assert cliente.post('/auth/logout', headers={'X-CSRF-Token': csrf}).status_code == 200
45:     assert cliente.get('/auth/me').status_code == 401
```

## tests/test_access.py::test_me_usuario_eliminado_rechazado

```python
48: def test_me_usuario_eliminado_rechazado(cliente):
49:     login(cliente)
50:     id_usuario = cliente.get('/auth/me').json()['id']
51:     repo = cliente.app.state.usuarios
52:     repo._usuarios.pop(__import__('uuid').UUID(id_usuario))
53:     assert cliente.get('/auth/me').status_code == 401
```

## tests/test_access.py::test_servicio_permite_panel_solo_con_autorizacion_explicita

```python
56: def test_servicio_permite_panel_solo_con_autorizacion_explicita(cliente):
57:     login(cliente)
58:     from uuid import UUID
59:     uid = UUID(cliente.get('/auth/me').json()['id'])
60:     class Autorizado:
61:         def tiene_asociacion_autorizada(self, usuario_id):
62:             return usuario_id == uid
63:     resultado = AccessService(cliente.app.state.usuarios, Autorizado()).consultar(uid)
64:     assert resultado.destino is DestinoAcceso.PANEL
```

## tests/test_access.py::test_autorizacion_ambigua_no_da_panel

```python
68: def test_autorizacion_ambigua_no_da_panel(cliente, respuesta):
69:     login(cliente)
70:     from uuid import UUID
71:     uid = UUID(cliente.get('/auth/me').json()['id'])
72:     class Ambigua:
73:         def tiene_asociacion_autorizada(self, usuario_id):
74:             return respuesta
75:     assert AccessService(cliente.app.state.usuarios, Ambigua()).consultar(uid).destino is DestinoAcceso.INCORPORACION_EMPRESARIAL
```

## tests/test_access.py::test_error_membership_falla_cerrado

```python
78: def test_error_membership_falla_cerrado(cliente):
79:     login(cliente)
80:     from uuid import UUID
81:     uid = UUID(cliente.get('/auth/me').json()['id'])
82:     class Rota:
83:         def tiene_asociacion_autorizada(self, usuario_id):
84:             raise RuntimeError('BD no disponible')
85:     assert AccessService(cliente.app.state.usuarios, Rota()).consultar(uid).destino is DestinoAcceso.INCORPORACION_EMPRESARIAL
```

## tests/test_access.py::test_usuario_ausente_servicio

```python
88: def test_usuario_ausente_servicio():
89:     app = create_app()
90:     with pytest.raises(UsuarioNoDisponible):
91:         app.state.access_service.consultar(uuid4())
```

## tests/test_companies_api.py::test_registro_y_consulta_publica_con_normalizacion

```python
38: def test_registro_y_consulta_publica_con_normalizacion(autorizado):
39:     client, headers = autorizado
40:     respuesta = client.post(URL, headers=headers, json={
41:         "nombre": " TecniRed  Sabana ", "ciudad": " Bogotá ",
42:         "nit": " 900123456-7 ", "sector": " Tecnología ",
43:     })
44:     assert respuesta.status_code == 201
45:     datos = respuesta.json()
46:     assert set(datos) == {"id", "nombre", "ciudad", "nit", "sector", "creado_en"}
47:     assert UUID(datos["id"]).version == 4
48:     assert datos["creado_en"].endswith("Z")
49:     assert datos["nombre"] == "TecniRed  Sabana" and datos["ciudad"] == "Bogotá"
50:     assert datos["nit"] == "900123456-7" and datos["sector"] == "Tecnología"
51:     consulta = client.get(URL + "/me")
52:     assert consulta.status_code == 200 and consulta.json() == datos
53:     usuario = client.app.state.usuarios.buscar_por_correo("empresa@example.com")
54:     assert client.app.state.empresas.buscar_por_usuario(usuario.id).id == UUID(datos["id"])
```

## tests/test_companies_api.py::test_limites_normalizados_y_opcionales_omitidos

```python
57: def test_limites_normalizados_y_opcionales_omitidos(autorizado):
58:     client, headers = autorizado
59:     respuesta = client.post(URL, headers=headers,
60:                            json={"nombre": " " + "á" * 150 + " ", "ciudad": "ñ" * 100})
61:     assert respuesta.status_code == 201
62:     assert len(respuesta.json()["nombre"]) == 150
63:     assert respuesta.json()["nit"] is None and respuesta.json()["sector"] is None
```

## tests/test_companies_api.py::test_opcionales_nulos_o_vacios

```python
67: def test_opcionales_nulos_o_vacios(autorizado, opcionales):
68:     client, headers = autorizado
69:     respuesta = client.post(URL, headers=headers, json={"nombre": "Empresa", "ciudad": "Cali", **opcionales})
70:     assert respuesta.status_code == 201
71:     assert respuesta.json()["nit"] is None and respuesta.json()["sector"] is None
```

## tests/test_companies_api.py::test_entrada_invalida_no_guarda

```python
79: def test_entrada_invalida_no_guarda(autorizado, cambio):
80:     client, headers = autorizado
81:     respuesta = client.post(URL, headers=headers, json={"nombre": "Empresa", "ciudad": "Cali", **cambio})
82:     assert respuesta.status_code == 422
83:     assert client.get(URL + "/me").status_code == 404
```

## tests/test_companies_api.py::test_sin_sesion_es_401

```python
87: def test_sin_sesion_es_401(cliente, metodo, ruta):
88:     kwargs = {"json": {"nombre": "Empresa", "ciudad": "Cali"}} if metodo == "post" else {}
89:     assert getattr(cliente, metodo)(ruta, **kwargs).status_code == 401
```

## tests/test_companies_api.py::test_sesion_no_vigente_rechazada

```python
93: def test_sesion_no_vigente_rechazada(autorizado, estado):
94:     client, headers = autorizado
95:     token = client.cookies.get("continuity_session")
96:     repo = client.app.state.sesiones
97:     if estado == "revocada":
98:         repo.invalidar(token)
99:     else:
100:         sesion = repo.buscar(token)
101:         fecha = sesion.creado_en - timedelta(hours=9 if estado == "expirada" else 1)
102:         repo.guardar(replace(sesion, creado_en=fecha, ultima_actividad_en=fecha,
103:                              expira_en=fecha + timedelta(hours=8)))
104:     assert client.post(URL, headers=headers, json={"nombre": "Empresa", "ciudad": "Cali"}).status_code == 401
105:     assert client.get(URL + "/me").status_code == 401
```

## tests/test_companies_api.py::test_csrf_requerido

```python
109: def test_csrf_requerido(autorizado, headers):
110:     client, _ = autorizado
111:     assert client.post(URL, headers=headers, json={"nombre": "Empresa", "ciudad": "Cali"}).status_code == 403
112:     assert client.get(URL + "/me").status_code == 404
```

## tests/test_companies_api.py::test_origen_rechazado

```python
116: def test_origen_rechazado(autorizado, origen):
117:     client, headers = autorizado
118:     assert client.post(URL, headers={**headers, **origen},
119:                        json={"nombre": "Empresa", "ciudad": "Cali"}).status_code == 403
120:     assert client.get(URL + "/me").status_code == 404
```

## tests/test_companies_api.py::test_duplicado_409_conserva_original

```python
123: def test_duplicado_409_conserva_original(autorizado):
124:     client, headers = autorizado
125:     original = client.post(URL, headers=headers, json={"nombre": "Original", "ciudad": "Cali"})
126:     assert original.status_code == 201
127:     assert client.post(URL, headers=headers, json={"nombre": "Otra", "ciudad": "Cali"}).status_code == 409
128:     assert client.get(URL + "/me").json() == original.json()
```

## tests/test_companies_api.py::test_aislamiento_y_csrf_ligado_a_sesion

```python
131: def test_aislamiento_y_csrf_ligado_a_sesion(autorizado):
132:     client, headers_a = autorizado
133:     datos = {"nombre": "Empresa A", "ciudad": "Cali", "nit": "900123456-7"}
134:     primera = client.post(URL, headers=headers_a, json=datos).json()
135:     headers_b = entrar(client, "otra@example.com")
136:     assert client.get(URL + "/me").status_code == 404
137:     assert client.post(URL, headers=headers_a, json=datos).status_code == 403
138:     segunda = client.post(URL, headers=headers_b, json={**datos, "nombre": "Empresa B"})
139:     assert segunda.status_code == 201 and segunda.json()["id"] != primera["id"]
140:     assert client.get(URL + "/me").json() == segunda.json()
```

## tests/test_companies_api.py::test_fallos_internos_son_500_sin_detalles

```python
144: def test_fallos_internos_son_500_sin_detalles(autorizado, monkeypatch, operacion):
145:     client, headers = autorizado
146: 
147:     def fallar(*args, **kwargs):
148:         raise RuntimeError("detalle-interno-no-publico")
149: 
150:     if operacion == "sesion":
151:         monkeypatch.setattr(client.app.state.session_service, "autenticar", fallar)
152:     elif operacion == "respuesta":
153:         monkeypatch.setattr(client.app.state.empresa_service, "consultar", lambda uid: object())
154:     else:
155:         monkeypatch.setattr(client.app.state.empresas, operacion, fallar)
156:     respuesta = (client.post(URL, headers=headers, json={"nombre": "Empresa", "ciudad": "Cali"})
157:                  if operacion == "crear" else client.get(URL + "/me"))
158:     assert respuesta.status_code == 500
159:     assert respuesta.json() == {"detail": "Operación de empresa temporalmente no disponible"}
160:     assert "detalle-interno" not in respuesta.text
```

## tests/test_companies_api.py::test_colision_de_guardado_devuelve_409

```python
163: def test_colision_de_guardado_devuelve_409(autorizado, monkeypatch):
164:     client, headers = autorizado
165: 
166:     def colision(empresa):
167:         raise ValueError("Empresa duplicada")
168: 
169:     monkeypatch.setattr(client.app.state.empresas, "crear", colision)
170:     assert client.post(URL, headers=headers, json={"nombre": "Empresa", "ciudad": "Cali"}).status_code == 409
```

## tests/test_companies_api.py::test_modo_postgres_compone_sin_conectar

```python
173: def test_modo_postgres_compone_sin_conectar(monkeypatch):
174:     import app.main as main
175:     from app.infrastructure.postgres_companies import PostgresCompanyRepository
176: 
177:     def no_conectar():
178:         pytest.fail("La composición no debe abrir conexiones")
179: 
180:     monkeypatch.setenv("CONTINUITY_STORAGE", "postgres")
181:     monkeypatch.setattr(main, "nueva_conexion", no_conectar)
182:     app = main.create_app()
183:     assert isinstance(app.state.empresas, PostgresCompanyRepository)
184:     assert isinstance(app.state.empresa_service, EmpresaService)
```

## tests/test_company_repositories.py::test_traduce_solo_unique_del_usuario

```python
27: def test_traduce_solo_unique_del_usuario(restriccion, tabla, esquema, duplicado):
28:     class Colision(errors.UniqueViolation):
29:         @property
30:         def diag(self):
31:             resultado = MagicMock()
32:             resultado.constraint_name = restriccion
33:             resultado.table_name = tabla
34:             resultado.schema_name = esquema
35:             return resultado
36: 
37:     error = Colision("detalle interno")
38:     conectar = MagicMock()
39:     conectar.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value.execute.side_effect = error
40:     repo = PostgresCompanyRepository(conectar)
41:     with pytest.raises(ValueError if duplicado else Colision) as resultado:
42:         repo.crear(empresa())
43:     if duplicado:
44:         assert str(resultado.value) == "Empresa duplicada" and resultado.value.__cause__ is error
45:     else:
46:         assert resultado.value is error
```

## tests/test_company_repositories.py::test_consulta_recupera_empresa_y_ausencia

```python
49: def test_consulta_recupera_empresa_y_ausencia():
50:     original = empresa()
51:     conectar = MagicMock()
52:     cursor = conectar.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
53:     cursor.fetchone.return_value = (original.id, original.usuario_id, original.nombre,
54:                                    original.ciudad, original.creado_en, original.nit, original.sector)
55:     repo = PostgresCompanyRepository(conectar)
56:     assert isinstance(repo, CompanyRepository)
57:     assert repo.buscar_por_usuario(original.usuario_id) == original
58:     cursor.fetchone.return_value = None
59:     assert repo.buscar_por_usuario(uuid4()) is None
```

## tests/test_company_repositories.py::test_memory_creacion_simultanea_no_sobrescribe

```python
62: def test_memory_creacion_simultanea_no_sobrescribe():
63:     from dataclasses import replace
64: 
65:     repo = MemoryCompanyRepository()
66:     assert isinstance(repo, CompanyRepository)
67:     primera = empresa()
68:     segunda = replace(primera, id=uuid4(), nombre="Otra")
69:     barrera = Barrier(2)
70: 
71:     def crear(valor):
72:         barrera.wait(timeout=10)
73:         try:
74:             repo.crear(valor)
75:             return valor
76:         except ValueError as exc:
77:             assert str(exc) == "Empresa duplicada"
78:             return None
79: 
80:     with ThreadPoolExecutor(max_workers=2) as executor:
81:         resultados = list(executor.map(crear, [primera, segunda]))
82:     ganadoras = [r for r in resultados if r is not None]
83:     assert len(ganadoras) == 1
84:     assert repo.buscar_por_usuario(primera.usuario_id) == ganadoras[0]
```

## tests/test_company_service.py::test_registro_genera_uuid_fecha_utc_y_asocia_usuario

```python
32: def test_registro_genera_uuid_fecha_utc_y_asocia_usuario(repo):
33:     usuario_id = uuid4()
34:     antes = datetime.now(timezone.utc)
35:     empresa = EmpresaService(repo).registrar(usuario_id, "TecniRed", "Bogotá")
36:     assert isinstance(repo, CompanyRepository)
37:     assert isinstance(empresa.id, UUID) and empresa.id.version == 4
38:     assert empresa.usuario_id == usuario_id
39:     assert empresa.nombre == "TecniRed" and empresa.ciudad == "Bogotá"
40:     assert empresa.creado_en.tzinfo is timezone.utc
41:     assert antes <= empresa.creado_en <= datetime.now(timezone.utc)
42:     assert repo.buscar_por_usuario(usuario_id) is empresa
43:     assert empresa.nit is None and empresa.sector is None
```

## tests/test_company_service.py::test_normaliza_extremos_y_conserva_espacios_internos

```python
46: def test_normaliza_extremos_y_conserva_espacios_internos(repo):
47:     empresa = EmpresaService(repo).registrar(
48:         uuid4(), " \tTecniRed  Sabana\n", "  Bogotá  D.C. ",
49:         nit=" 900123456-7 ", sector=" Servicios  tecnológicos ",
50:     )
51:     assert empresa.nombre == "TecniRed  Sabana"
52:     assert empresa.ciudad == "Bogotá  D.C."
53:     assert empresa.nit == "900123456-7"
54:     assert empresa.sector == "Servicios  tecnológicos"
```

## tests/test_company_service.py::test_opcionales_vacios_se_normalizan_a_none

```python
57: def test_opcionales_vacios_se_normalizan_a_none(repo):
58:     empresa = EmpresaService(repo).registrar(uuid4(), "Empresa", "Cali", " \t", "\n ")
59:     assert empresa.nit is None and empresa.sector is None
```

## tests/test_company_service.py::test_limites_inclusivos_se_validan_despues_de_normalizar

```python
62: def test_limites_inclusivos_se_validan_despues_de_normalizar(repo):
63:     empresa = EmpresaService(repo).registrar(
64:         uuid4(), " " + "á" * 150 + " ", " " + "ñ" * 100 + " ",
65:         " " + "1" * 20 + " ", " " + "é" * 100 + " ",
66:     )
67:     assert (len(empresa.nombre), len(empresa.ciudad), len(empresa.nit),
68:             len(empresa.sector)) == (150, 100, 20, 100)
```

## tests/test_company_service.py::test_datos_invalidos_no_guardan_empresa

```python
78: def test_datos_invalidos_no_guardan_empresa(repo, campo, valor):
79:     datos = dict(nombre="Empresa", ciudad="Bogotá")
80:     datos[campo] = valor
81:     with pytest.raises(EmpresaInvalida, match=campo):
82:         EmpresaService(repo).registrar(uuid4(), **datos)
83:     assert repo.empresas == {}
```

## tests/test_company_service.py::test_entidad_impide_identificadores_y_fecha_invalidos

```python
90: def test_entidad_impide_identificadores_y_fecha_invalidos(cambios):
91:     datos = dict(id=uuid4(), usuario_id=uuid4(), nombre="Empresa", ciudad="Cali",
92:                  creado_en=datetime.now(timezone.utc))
93:     datos.update(cambios)
94:     with pytest.raises(ValueError):
95:         Empresa(**datos)
```

## tests/test_company_service.py::test_entidad_normaliza_fecha_a_utc_y_es_inmutable

```python
98: def test_entidad_normaliza_fecha_a_utc_y_es_inmutable():
99:     fecha = datetime(2026, 11, 7, 10, tzinfo=timezone(timedelta(hours=-5)))
100:     empresa = Empresa(uuid4(), uuid4(), " Empresa ", " Cali ", fecha)
101:     assert empresa.nombre == "Empresa" and empresa.ciudad == "Cali"
102:     assert empresa.creado_en == datetime(2026, 11, 7, 15, tzinfo=timezone.utc)
103:     assert empresa.creado_en.tzinfo is timezone.utc
104:     with pytest.raises(FrozenInstanceError):
105:         empresa.nombre = "Otra"
```

## tests/test_company_service.py::test_consulta_sin_empresa_devuelve_none

```python
108: def test_consulta_sin_empresa_devuelve_none(repo):
109:     assert EmpresaService(repo).consultar(uuid4()) is None
110:     assert repo.empresas == {}
```

## tests/test_company_service.py::test_segundo_registro_no_sobrescribe_empresa

```python
113: def test_segundo_registro_no_sobrescribe_empresa(repo):
114:     servicio = EmpresaService(repo)
115:     usuario_id = uuid4()
116:     original = servicio.registrar(usuario_id, "Original", "Cali")
117:     with pytest.raises(EmpresaDuplicada):
118:         servicio.registrar(usuario_id, "Otra", "Bogotá")
119:     assert servicio.consultar(usuario_id) is original
120:     assert len(repo.empresas) == 1
```

## tests/test_company_service.py::test_usuarios_aislados_pueden_compartir_nit

```python
123: def test_usuarios_aislados_pueden_compartir_nit(repo):
124:     servicio = EmpresaService(repo)
125:     primero, segundo = uuid4(), uuid4()
126:     empresa_a = servicio.registrar(primero, "Empresa A", "Cali", "900123456-7")
127:     empresa_b = servicio.registrar(segundo, "Empresa B", "Bogotá", "900123456-7")
128:     assert empresa_a.id != empresa_b.id
129:     assert servicio.consultar(primero) is empresa_a
130:     assert servicio.consultar(segundo) is empresa_b
131:     assert servicio.consultar(uuid4()) is None
```

## tests/test_company_service.py::test_colision_al_crear_se_traduce_a_duplicado

```python
134: def test_colision_al_crear_se_traduce_a_duplicado(repo):
135:     class RepoColision(CompanyRepositoryFake):
136:         def buscar_por_usuario(self, usuario_id):
137:             # Simula una consulta que no vio el registro recién creado.
138:             return None
139: 
140:     repo = RepoColision()
141:     servicio = EmpresaService(repo)
142:     usuario_id = uuid4()
143:     original = servicio.registrar(usuario_id, "Original", "Cali")
144:     with pytest.raises(EmpresaDuplicada):
145:         servicio.registrar(usuario_id, "Otra", "Bogotá")
146:     assert repo.empresas == {usuario_id: original}
```

## tests/test_company_service.py::test_errores_de_repositorio_no_se_confunden_con_duplicidad

```python
150: def test_errores_de_repositorio_no_se_confunden_con_duplicidad(error):
151:     class RepoFalla(CompanyRepositoryFake):
152:         def crear(self, empresa):
153:             raise error
154: 
155:     repo = RepoFalla()
156:     with pytest.raises(type(error)) as resultado:
157:         EmpresaService(repo).registrar(uuid4(), "Empresa", "Cali")
158:     assert resultado.value is error
159:     assert repo.empresas == {}
```

## tests/test_foundation.py::test_usuario_valido_activo_cliente

```python
17: def test_usuario_valido_activo_cliente():
18:     usuario, credencial = cuenta()
19:     assert usuario.estado == EstadoCuenta.ACTIVA
20:     assert usuario.rol == "CLIENTE"
21:     assert credencial.usuario_id == usuario.id
```

## tests/test_foundation.py::test_no_existe_no_es_estado_persistible

```python
24: def test_no_existe_no_es_estado_persistible():
25:     with pytest.raises(ValueError):
26:         Usuario(uuid4(), "Cliente", "a@b.co", NOW, estado=EstadoCuenta.NO_EXISTE)
```

## tests/test_foundation.py::test_cuenta_inexistente_y_activa

```python
29: def test_cuenta_inexistente_y_activa():
30:     repo, sesiones = MemoryUserRepository(), MemorySessionRepository()
31:     servicio = AuthService(repo, sesiones)
32:     assert servicio.estado_cuenta("ninguno@ejemplo.com") == EstadoCuenta.NO_EXISTE
33:     user, credential = cuenta()
34:     repo.crear_cuenta(user, credential)
35:     assert servicio.estado_cuenta(user.email_normalizado) == EstadoCuenta.ACTIVA
```

## tests/test_foundation.py::test_registro_dual_sin_parcialidad_si_ids_no_coinciden

```python
38: def test_registro_dual_sin_parcialidad_si_ids_no_coinciden():
39:     repo = MemoryUserRepository()
40:     user, _ = cuenta()
41:     with pytest.raises(ValueError):
42:         repo.crear_cuenta(user, Credencial(uuid4(), "hash"))
43:     assert repo.buscar_por_correo(user.email_normalizado) is None
44:     assert repo.buscar_credencial(user.id) is None
```

## tests/test_foundation.py::test_correo_duplicado_no_sobrescribe_credencial

```python
47: def test_correo_duplicado_no_sobrescribe_credencial():
48:     repo = MemoryUserRepository()
49:     user, credencial = cuenta()
50:     repo.crear_cuenta(user, credencial)
51:     otro, otra_credencial = cuenta()
52:     with pytest.raises(ValueError):
53:         repo.crear_cuenta(otro, otra_credencial)
54:     assert repo.buscar_credencial(user.id) == credencial
55:     assert repo.buscar_credencial(otro.id) is None
```

## tests/test_foundation.py::test_sesion_vigente_y_expirada

```python
58: def test_sesion_vigente_y_expirada():
59:     user, _ = cuenta()
60:     sesion = Sesion("token-opaco-de-prueba", user.id, NOW, NOW + timedelta(hours=8), NOW)
61:     repo = MemorySessionRepository()
62:     repo.guardar(sesion)
63:     servicio = AuthService(MemoryUserRepository(), repo)
64:     assert servicio.estado_sesion(sesion.id, NOW) == EstadoSesion.VIGENTE
65:     assert servicio.estado_sesion(sesion.id, NOW + timedelta(hours=8)) == EstadoSesion.EXPIRADA
```

## tests/test_foundation.py::test_invalidacion_impide_reutilizacion

```python
68: def test_invalidacion_impide_reutilizacion():
69:     repo = MemorySessionRepository()
70:     uid = uuid4()
71:     repo.guardar(Sesion("abc", uid, NOW, NOW + timedelta(hours=1), NOW))
72:     repo.invalidar("abc")
73:     assert AuthService(MemoryUserRepository(), repo).estado_sesion("abc", NOW) == EstadoSesion.EXPIRADA
```

## tests/test_foundation.py::test_fechas_sin_zona_horaria_se_rechazan

```python
76: def test_fechas_sin_zona_horaria_se_rechazan():
77:     with pytest.raises(ValueError):
78:         Usuario(uuid4(), "Cliente", "a@b.co", datetime(2026, 1, 1))
```

## tests/test_foundation.py::test_contratos_y_autorizacion_cerrada

```python
81: def test_contratos_y_autorizacion_cerrada():
82:     usuarios, sesiones, membresia = MemoryUserRepository(), MemorySessionRepository(), NoMembershipLookup()
83:     assert isinstance(usuarios, UserRepository)
84:     assert isinstance(sesiones, SessionRepository)
85:     assert isinstance(membresia, MembershipLookup)
86:     assert not membresia.tiene_asociacion_autorizada(uuid4())
```

## tests/test_frontend_f01.py::test_pagina_login_se_sirve_con_utf8_y_meta_basicas

```python
19: def test_pagina_login_se_sirve_con_utf8_y_meta_basicas():
20:     response = TestClient(create_app()).get("/login")
21:     assert response.status_code == 200
22:     assert "text/html" in response.headers["content-type"]
23:     assert '<meta charset="UTF-8">' in response.text
24:     assert 'lang="es"' in response.text
25:     assert 'name="viewport"' in response.text
26:     assert 'name="robots" content="noindex, nofollow"' in response.text
```

## tests/test_frontend_f01.py::test_semantica_un_solo_h1_y_campos_etiquetados

```python
29: def test_semantica_un_solo_h1_y_campos_etiquetados():
30:     parsed = Elements()
31:     parsed.feed((ROOT / "templates/login.html").read_text(encoding="utf8"))
32:     assert parsed.tags.count("h1") == 1
33:     for tag in ("header", "main", "section", "aside", "footer", "form"):
34:         assert tag in parsed.tags
35:     ids = {d["id"] for _, d in parsed.attrs if "id" in d}
36:     labels = {d["for"] for t, d in parsed.attrs if t == "label"}
37:     assert {"email", "password"} <= ids
38:     assert {"email", "password"} <= labels
```

## tests/test_frontend_f01.py::test_codigo_y_estilos_externos

```python
41: def test_codigo_y_estilos_externos():
42:     doc = (ROOT / "templates/login.html").read_text(encoding="utf8")
43:     assert "<style" not in doc and "<script>" not in doc
44:     assert "style=" not in doc and "onclick=" not in doc
45:     with TestClient(create_app()) as client:
46:         for path in ("/static/css/base.css", "/static/css/login.css", "/static/js/login.js"):
47:             assert client.get(path).status_code == 200
```

## tests/test_frontend_f01.py::test_api_anterior_continua_disponible

```python
50: def test_api_anterior_continua_disponible():
51:     with TestClient(create_app()) as client:
52:         assert client.get("/openapi.json").status_code == 200
53:         assert client.get("/auth/me").status_code == 401
54:         assert client.get("/").headers["content-type"].startswith("text/html")
```

## tests/test_frontend_integrated.py::test_vistas_y_metadatos

```python
11: def test_vistas_y_metadatos():
12:     with client() as c:
13:         for path, form_id in (("/login", "login-form"), ("/register", "register-form"), ("/access", None)):
14:             r = c.get(path)
15:             assert r.status_code == 200
16:             assert 'lang="es"' in r.text
17:             assert 'charset="UTF-8"' in r.text
18:             assert len(re.findall(r"<h1(?:\s|>)", r.text, re.I)) == 1
19:             assert '<style' not in r.text and '<script>' not in r.text
20:             assert 'noindex' in r.text
21:             if form_id:
22:                 assert f'id="{form_id}"' in r.text
```

## tests/test_frontend_integrated.py::test_recursos_estaticos_por_separado

```python
25: def test_recursos_estaticos_por_separado():
26:     with client() as c:
27:         for resource in ('common.js', 'login.js', 'register.js', 'access.js'):
28:             r = c.get('/static/js/' + resource)
29:             assert r.status_code == 200
30:         for resource in ('base.css', 'login.css'):
31:             assert c.get('/static/css/' + resource).status_code == 200
```

## tests/test_frontend_integrated.py::test_registro_login_contexto_y_logout

```python
34: def test_registro_login_contexto_y_logout():
35:     with client() as c:
36:         payload = {"nombre": "Empresa de Prueba", "email": "integrada@example.com", "password": "ClaveMuySegura2026!", "confirmacion_password": "ClaveMuySegura2026!"}
37:         registered = c.post('/auth/register', json=payload)
38:         assert registered.status_code == 201
39:         login = c.post('/auth/login', json={"email": payload['email'], "password": payload['password']})
40:         assert login.status_code == 200
41:         assert 'httponly' in login.headers['set-cookie'].lower()
42:         assert 'samesite=lax' in login.headers['set-cookie'].lower()
43:         me = c.get('/auth/me')
44:         assert me.status_code == 200
45:         assert me.json()['destino'] == 'INCORPORACION_EMPRESARIAL'
46:         no_csrf = c.post('/auth/logout')
47:         assert no_csrf.status_code == 403
48:         token = c.get('/auth/csrf').json()['csrf_token']
49:         out = c.post('/auth/logout', headers={'X-CSRF-Token': token})
50:         assert out.status_code == 200
51:         assert c.get('/auth/me').status_code == 401
```

## tests/test_frontend_integrated.py::test_sin_autenticacion_no_hay_contexto

```python
54: def test_sin_autenticacion_no_hay_contexto():
55:     with client() as c:
56:         assert c.get('/auth/me').status_code == 401
57:         assert c.get('/auth/csrf').status_code == 401
```

## tests/test_frontend_integrated.py::test_login_mensaje_generico

```python
60: def test_login_mensaje_generico():
61:     with client() as c:
62:         r = c.post('/auth/login', json={'email': 'missing@example.com', 'password': 'x'})
63:         assert r.status_code == 401
64:         assert r.json()['detail'] == 'Credenciales inválidas'
```

## tests/test_frontend_integrated.py::test_registro_rechaza_contrasenas_distintas

```python
67: def test_registro_rechaza_contrasenas_distintas():
68:     with client() as c:
69:         r = c.post('/auth/register', json={'nombre':'Ejemplo','email':'other@example.com','password':'ClaveMuySegura2026!','confirmacion_password':'otra-contraseña'})
70:         assert r.status_code == 422
```

## tests/test_frontend_integrated.py::test_no_se_exponen_secretos_en_me

```python
73: def test_no_se_exponen_secretos_en_me():
74:     with client() as c:
75:         payload={'nombre':'Ejemplo','email':'secret@example.com','password':'ClaveMuySegura2026!','confirmacion_password':'ClaveMuySegura2026!'}
76:         c.post('/auth/register', json=payload)
77:         c.post('/auth/login', json={'email': payload['email'], 'password':payload['password']})
78:         body = c.get('/auth/me').text.lower()
79:         assert 'password' not in body and 'token' not in body and 'hash' not in body
```

## tests/test_frontend_integrated.py::test_csrf_incorrecto_no_cierra_sesion

```python
82: def test_csrf_incorrecto_no_cierra_sesion():
83:     with client() as c:
84:         p={'nombre':'Otro','email':'csrf@example.com','password':'ClaveMuySegura2026!','confirmacion_password':'ClaveMuySegura2026!'}
85:         c.post('/auth/register', json=p)
86:         c.post('/auth/login', json={'email':p['email'],'password':p['password']})
87:         assert c.post('/auth/logout', headers={'X-CSRF-Token':'invalido'}).status_code == 403
88:         assert c.get('/auth/me').status_code == 200
```

## tests/test_frontend_rf02.py::test_empresa_semantica_oculta_y_campos_accesibles

```python
25: def test_empresa_semantica_oculta_y_campos_accesibles():
26:     html = (ROOT / "app/templates/access.html").read_text(encoding="utf-8")
27:     elements = Elements(html).elements
28:     ids = {attrs["id"]: attrs for _, attrs in elements if "id" in attrs}
29:     assert sum(tag == "h1" for tag, _ in elements) == 1
30:     assert 'lang="es"' in html and 'charset="UTF-8"' in html
31:     assert "hidden" in ids["company-section"]
32:     assert ids["show-company"]["aria-controls"] == "company-section"
33:     assert ids["show-company"]["aria-expanded"] == "false"
34:     labels = {attrs["for"] for tag, attrs in elements if tag == "label"}
35:     for field, length, required in [("name", 150, True), ("city", 100, True),
36:                                     ("nit", 20, False), ("sector", 100, False)]:
37:         key = "company-" + field
38:         assert key in labels
39:         assert ids[key]["maxlength"] == str(length)
40:         assert ("required" in ids[key]) == required
41:     assert sum(tag == "dt" for tag, _ in elements) == 4
42:     assert sum(tag == "dd" for tag, _ in elements) == 4
43:     assert "hidden" in ids["company-form"] and "hidden" in ids["company-details"]
44:     assert ids["company-feedback"]["aria-live"] == "polite"
45:     assert '<script>' not in html and '<style' not in html and 'onclick=' not in html
```

## tests/test_frontend_rf02.py::test_access_y_recursos_empresa_se_sirven

```python
56: def test_access_y_recursos_empresa_se_sirven(client):
57:     assert 'id="company-section"' in client.get("/access").text
58:     for path in ["/static/css/company.css", "/static/css/base.css", "/static/css/login.css",
59:                  "/static/js/access.js", "/static/js/common.js"]:
60:         assert client.get(path).status_code == 200
```

## tests/test_frontend_rf02.py::test_flujo_http_access_empresa_y_nueva_sesion

```python
64: def test_flujo_http_access_empresa_y_nueva_sesion(client, opcionales):
65:     """HTTP real, sin ejecutar JS ni afirmar persistencia PostgreSQL."""
66:     credentials = {"email": "frontend@example.com", "password": "ClaveRF02!2026_Segura"}
67:     assert client.post("/auth/register", json={"nombre": "Cliente", **credentials,
68:                        "confirmacion_password": credentials["password"]}).status_code == 201
69:     assert client.post("/auth/login", json=credentials).status_code == 200
70:     assert client.get("/access").status_code == 200
71:     assert client.get("/auth/companies/me").status_code == 404
72:     payload = {"nombre": " Empresa Bogotá ", "ciudad": " Bogotá ", **opcionales}
73:     assert client.post("/auth/companies", json=payload).status_code == 403
74:     token = client.get("/auth/csrf").json()["csrf_token"]
75:     headers = {"X-CSRF-Token": token}
76:     result = client.post("/auth/companies", headers=headers, json=payload)
77:     assert result.status_code == 201
78:     company = result.json()
79:     assert company["nombre"] == "Empresa Bogotá"
80:     assert company["nit"] == opcionales.get("nit")
81:     assert client.post("/auth/companies", headers=headers, json=payload).status_code == 409
82:     assert client.post("/auth/logout", headers=headers).status_code == 200
83:     assert client.get("/auth/companies/me").status_code == 401
84:     assert client.post("/auth/login", json=credentials).status_code == 200
85:     assert client.get("/auth/companies/me").json() == company
```

## tests/test_frontend_rf02.py::test_javascript_rf02_con_dom_simulado

```python
88: def test_javascript_rf02_con_dom_simulado():
89:     node = shutil.which("node")
90:     if node is None:
91:         pytest.skip("Node no disponible para ejecutar JavaScript; no requiere instalar paquetes")
92:     result = subprocess.run([node, "tests/frontend_rf02.test.cjs"], cwd=ROOT,
93:                             text=True, capture_output=True, timeout=30)
94:     assert result.returncode == 0, result.stdout + result.stderr
```

## tests/test_login.py::test_login_correcto_crea_sesion_y_cookie

```python
21: def test_login_correcto_crea_sesion_y_cookie(cliente):
22:     r = cliente.post("/auth/login", json={"email": "CLIENTE@EJEMPLO.COM", "password": PASSWORD})
23:     assert r.status_code == 200
24:     assert r.json() == {"mensaje": "Autenticación exitosa"}
25:     cookie = r.headers["set-cookie"]
26:     assert "HttpOnly" in cookie and "Secure" in cookie and "SameSite=lax" in cookie
27:     assert "Path=/auth" in cookie
28:     token = cliente.cookies.get("continuity_session")
29:     assert token and len(token) >= 40
30:     assert PASSWORD not in r.text and token not in r.text
31:     sesion = cliente.app.state.sesiones.buscar(token)
32:     assert sesion is not None
33:     assert sesion.estado_en(datetime.now(timezone.utc)) is EstadoSesion.VIGENTE
34:     assert timedelta(hours=7, minutes=59) < sesion.expira_en - sesion.creado_en <= timedelta(hours=8)
```

## tests/test_login.py::test_login_invalido_mensaje_generico_y_sin_cookie

```python
41: def test_login_invalido_mensaje_generico_y_sin_cookie(cliente, email, password):
42:     r = cliente.post("/auth/login", json={"email": email, "password": password})
43:     assert r.status_code == 401 and r.json()["detail"] == "Credenciales inválidas"
44:     assert "set-cookie" not in r.headers
45:     assert cliente.app.state.sesiones._sesiones == {}
```

## tests/test_login.py::test_limitador_ip_y_correo

```python
48: def test_limitador_ip_y_correo(cliente):
49:     for _ in range(5):
50:         assert cliente.post("/auth/login", json={"email": "cliente@ejemplo.com", "password": "errada"}).status_code == 401
51:     r = cliente.post("/auth/login", json={"email": "cliente@ejemplo.com", "password": PASSWORD})
52:     assert r.status_code == 429 and r.headers["retry-after"] == "900"
53:     # Otro correo tampoco evade el límite por IP.
54:     assert cliente.post("/auth/login", json={"email": "otro@ejemplo.com", "password": "errada"}).status_code == 429
```

## tests/test_login.py::test_sesiones_distintas_por_login

```python
57: def test_sesiones_distintas_por_login(cliente):
58:     body = {"email": "cliente@ejemplo.com", "password": PASSWORD}
59:     assert cliente.post("/auth/login", json=body).status_code == 200
60:     token1 = cliente.cookies.get("continuity_session")
61:     assert cliente.post("/auth/login", json=body).status_code == 200
62:     token2 = cliente.cookies.get("continuity_session")
63:     assert token1 != token2
```

## tests/test_login.py::test_password_no_se_expone_en_validacion

```python
66: def test_password_no_se_expone_en_validacion(cliente):
67:     r = cliente.post("/auth/login", json={"email": "cliente@ejemplo.com", "password": PASSWORD, "rol": "ADMIN"})
68:     assert r.status_code == 422 and "set-cookie" not in r.headers
```

## tests/test_login.py::test_no_se_guarda_sesion_si_falla_validacion

```python
71: def test_no_se_guarda_sesion_si_falla_validacion(cliente):
72:     class RepoFalla:
73:         def guardar(self, sesion):
74:             raise RuntimeError("detalle interno")
75:     cliente.app.state.login_service._sesiones = RepoFalla()
76:     r = cliente.post("/auth/login", json={"email": "cliente@ejemplo.com", "password": PASSWORD})
77:     assert r.status_code == 503 and "detalle interno" not in r.text and "set-cookie" not in r.headers
```

## tests/test_login.py::test_credencial_inexistente_no_autentica

```python
80: def test_credencial_inexistente_no_autentica(cliente):
81:     repo = cliente.app.state.usuarios
82:     usuario = repo.buscar_por_correo("cliente@ejemplo.com")
83:     repo._credenciales.pop(usuario.id)
84:     r = cliente.post("/auth/login", json={"email": "cliente@ejemplo.com", "password": PASSWORD})
85:     assert r.status_code == 401
```

## tests/test_postgres_companies.py::test_pg_persistencia_tras_reconexion

```python
77: def test_pg_persistencia_tras_reconexion(conectar, usuario):
78:     empresa = nueva_empresa(usuario.id)
79:     PostgresCompanyRepository(conectar).crear(empresa)
80:     assert PostgresCompanyRepository(conectar).buscar_por_usuario(usuario.id) == empresa
```

## tests/test_postgres_companies.py::test_pg_opcionales_y_aislamiento

```python
83: def test_pg_opcionales_y_aislamiento(conectar, usuario):
84:     repo = PostgresCompanyRepository(conectar)
85:     empresa = nueva_empresa(usuario.id, nit=None, sector=None)
86:     repo.crear(empresa)
87:     assert repo.buscar_por_usuario(usuario.id) == empresa
88:     assert repo.buscar_por_usuario(uuid4()) is None
```

## tests/test_postgres_companies.py::test_pg_fk_rechaza_usuario_inexistente

```python
91: def test_pg_fk_rechaza_usuario_inexistente(conectar):
92:     repo = PostgresCompanyRepository(conectar)
93:     usuario_id = uuid4()
94:     with pytest.raises(psycopg.errors.ForeignKeyViolation):
95:         repo.crear(nueva_empresa(usuario_id))
96:     assert repo.buscar_por_usuario(usuario_id) is None
```

## tests/test_postgres_companies.py::test_pg_unique_usuario_sin_sobrescritura

```python
99: def test_pg_unique_usuario_sin_sobrescritura(conectar, usuario):
100:     repo = PostgresCompanyRepository(conectar)
101:     original = nueva_empresa(usuario.id)
102:     repo.crear(original)
103:     with pytest.raises(ValueError, match="^Empresa duplicada$"):
104:         repo.crear(replace(original, id=uuid4(), nombre="Otra"))
105:     assert repo.buscar_por_usuario(usuario.id) == original
```

## tests/test_postgres_companies.py::test_pg_colision_concurrente

```python
108: def test_pg_colision_concurrente(conectar, usuario):
109:     empresas = [nueva_empresa(usuario.id), nueva_empresa(usuario.id, nombre="Otra")]
110:     barrera = Barrier(2)
111: 
112:     def crear(empresa):
113:         barrera.wait(timeout=10)
114:         try:
115:             PostgresCompanyRepository(conectar).crear(empresa)
116:             return empresa
117:         except ValueError as exc:
118:             assert str(exc) == "Empresa duplicada"
119:             return None
120: 
121:     with ThreadPoolExecutor(max_workers=2) as executor:
122:         resultados = list(executor.map(crear, empresas))
123:     ganadoras = [r for r in resultados if r is not None]
124:     assert len(ganadoras) == 1
125:     assert PostgresCompanyRepository(conectar).buscar_por_usuario(usuario.id) == ganadoras[0]
```

## tests/test_postgres_companies.py::test_pg_fallo_de_insercion_no_deja_registro

```python
128: def test_pg_fallo_de_insercion_no_deja_registro(conectar, usuario):
129:     repo = PostgresCompanyRepository(conectar)
130:     with pytest.raises((psycopg.Error, ValueError)):
131:         repo.crear(nueva_empresa(usuario.id, nit="invalido\x00"))
132:     assert repo.buscar_por_usuario(usuario.id) is None
133:     valida = nueva_empresa(usuario.id)
134:     repo.crear(valida)
135:     assert repo.buscar_por_usuario(usuario.id) == valida
```

## tests/test_postgres_companies.py::test_pg_permisos_minimos

```python
138: def test_pg_permisos_minimos(conectar):
139:     with conectar() as conn:
140:         with conn.cursor() as cur:
141:             cur.execute("""SELECT has_table_privilege(current_user, 'public.empresas', 'SELECT'),
142:                                   has_table_privilege(current_user, 'public.empresas', 'INSERT'),
143:                                   has_table_privilege(current_user, 'public.empresas', 'UPDATE'),
144:                                   has_table_privilege(current_user, 'public.empresas', 'DELETE')""")
145:             assert cur.fetchone() == (True, True, False, False)
```

## tests/test_postgres_companies.py::test_pg_api_nueva_aplicacion_y_nueva_sesion

```python
148: def test_pg_api_nueva_aplicacion_y_nueva_sesion(conectar, monkeypatch):
149:     import app.main as main
150: 
151:     monkeypatch.setenv("CONTINUITY_STORAGE", "postgres")
152:     monkeypatch.setenv("CONTINUITY_ENV", "production")
153:     monkeypatch.setattr(main, "nueva_conexion", conectar)
154:     correo, clave = f"rf02-api-{uuid4().hex}@example.com", "PruebaRF02!2026_Segura"
155:     with TestClient(main.create_app(), base_url="https://testserver") as client:
156:         assert client.post("/auth/register", json={"nombre": "Cliente RF02", "email": correo,
157:                            "password": clave, "confirmacion_password": clave}).status_code == 201
158:         assert client.post("/auth/login", json={"email": correo, "password": clave}).status_code == 200
159:         csrf = client.get("/auth/csrf").json()["csrf_token"]
160:         headers = {"X-CSRF-Token": csrf}
161:         datos = {"nombre": "Empresa persistida", "ciudad": "Bogotá"}
162:         respuesta = client.post("/auth/companies", headers=headers, json=datos)
163:         assert respuesta.status_code == 201
164:         original = respuesta.json()
165:         assert client.post("/auth/companies", headers=headers, json=datos).status_code == 409
166:         assert client.post("/auth/logout", headers=headers).status_code == 200
167:     with TestClient(main.create_app(), base_url="https://testserver") as client:
168:         assert client.post("/auth/login", json={"email": correo, "password": clave}).status_code == 200
169:         respuesta = client.get("/auth/companies/me")
170:         assert respuesta.status_code == 200 and respuesta.json() == original
```

## tests/test_quality.py::test_auditoria_cubre_registro_login_y_logout_sin_secretos

```python
17: def test_auditoria_cubre_registro_login_y_logout_sin_secretos(caplog):
18:     with caplog.at_level(logging.INFO, logger='continuity.audit'):
19:         with TestClient(create_app(), base_url='https://testserver') as client:
20:             assert registrar(client).status_code == 201
21:             assert registrar(client).status_code == 409
22:             assert client.post('/auth/login', json={'email': CORREO, 'password': 'incorrecta'}).status_code == 401
23:             assert client.post('/auth/login', json={'email': CORREO, 'password': CLAVE}).status_code == 200
24:             csrf = client.get('/auth/csrf').json()['csrf_token']
25:             cookie = client.cookies.get('continuity_session')
26:             assert client.post('/auth/logout', headers={'X-CSRF-Token': csrf}).status_code == 200
27:     mensajes = [r.getMessage() for r in caplog.records if r.name == 'continuity.audit']
28:     assert len(mensajes) == 5
29:     assert 'evento=registro resultado=exitoso codigo_http=201' in mensajes
30:     assert 'evento=registro resultado=fallido codigo_http=409' in mensajes
31:     assert 'evento=inicio_sesion resultado=fallido codigo_http=401' in mensajes
32:     assert 'evento=inicio_sesion resultado=exitoso codigo_http=200' in mensajes
33:     assert 'evento=cierre_sesion resultado=exitoso codigo_http=200' in mensajes
34:     texto = '\n'.join(mensajes)
35:     for secreto in (CLAVE, CORREO, csrf, cookie, 'incorrecta'):
36:         assert secreto not in texto
```

## tests/test_quality.py::test_auditoria_validacion_rechazada_sin_datos_sensibles

```python
39: def test_auditoria_validacion_rechazada_sin_datos_sensibles(caplog):
40:     with caplog.at_level(logging.INFO, logger='continuity.audit'):
41:         with TestClient(create_app(), base_url='https://testserver') as client:
42:             r = client.post('/auth/register', json={'nombre': 'A', 'email': CORREO,
43:                 'password': 'corta', 'confirmacion_password': 'corta'})
44:             assert r.status_code == 422
45:     assert 'evento=registro resultado=fallido codigo_http=422' in caplog.text
46:     assert CORREO not in caplog.text and 'corta' not in caplog.text
```

## tests/test_quality.py::test_logout_sin_csrf_es_rechazado_y_auditado

```python
49: def test_logout_sin_csrf_es_rechazado_y_auditado(caplog):
50:     with caplog.at_level(logging.INFO, logger='continuity.audit'):
51:         with TestClient(create_app(), base_url='https://testserver') as client:
52:             assert registrar(client).status_code == 201
53:             assert client.post('/auth/login', json={'email': CORREO, 'password': CLAVE}).status_code == 200
54:             assert client.post('/auth/logout').status_code == 403
55:             assert client.get('/auth/session').status_code == 200
56:     assert 'evento=cierre_sesion resultado=fallido codigo_http=403' in caplog.text
```

## tests/test_quality.py::test_logout_no_permite_reutilizar_cookie_anterior

```python
59: def test_logout_no_permite_reutilizar_cookie_anterior():
60:     with TestClient(create_app(), base_url='https://testserver') as client:
61:         registrar(client)
62:         client.post('/auth/login', json={'email': CORREO, 'password': CLAVE})
63:         original = client.cookies.get('continuity_session')
64:         csrf = client.get('/auth/csrf').json()['csrf_token']
65:         assert client.post('/auth/logout', headers={'X-CSRF-Token': csrf}).status_code == 200
66:         client.cookies.set('continuity_session', original, path='/auth')
67:         assert client.get('/auth/session').status_code == 401
```

## tests/test_registration.py::test_registro_valido_sin_inicio_de_sesion

```python
25: def test_registro_valido_sin_inicio_de_sesion(cliente):
26:     r = cliente.post("/auth/register", json=datos())
27:     assert r.status_code == 201
28:     assert r.json()["email"] == "cliente@ejemplo.com"
29:     assert r.json()["nombre"] == "Empresa Cliente"
30:     assert r.json()["estado"] == "ACTIVA"
31:     assert r.json()["rol"] == "CLIENTE"
32:     assert "password" not in r.json() and "password_hash" not in r.json()
33:     assert "set-cookie" not in r.headers
34:     usuario = cliente.app.state.usuarios.buscar_por_correo("cliente@ejemplo.com")
35:     hash_almacenado = cliente.app.state.usuarios.buscar_credencial(usuario.id).password_hash
36:     assert hash_almacenado != PASSWORD
37:     assert hash_almacenado.startswith("$argon2id$")
38:     assert Argon2PasswordHasher().verificar(PASSWORD, hash_almacenado)
39:     assert not Argon2PasswordHasher().verificar("incorrecta", hash_almacenado)
```

## tests/test_registration.py::test_correo_duplicado_case_insensitive

```python
42: def test_correo_duplicado_case_insensitive(cliente):
43:     assert cliente.post("/auth/register", json=datos()).status_code == 201
44:     assert cliente.post("/auth/register", json=datos(email="cliente@EJEMPLO.com")).status_code == 409
```

## tests/test_registration.py::test_datos_invalidos

```python
53: def test_datos_invalidos(cliente, changes):
54:     assert cliente.post("/auth/register", json=datos(**changes)).status_code == 422
55:     assert cliente.app.state.usuarios.buscar_por_correo("cliente@ejemplo.com") is None
```

## tests/test_registration.py::test_campos_extra_rechazados

```python
58: def test_campos_extra_rechazados(cliente):
59:     assert cliente.post("/auth/register", json=datos(rol="ADMIN")).status_code == 422
```

## tests/test_registration.py::test_fallo_del_hash_no_crea_usuario

```python
62: def test_fallo_del_hash_no_crea_usuario():
63:     class HashFalla:
64:         def generar_hash(self, password):
65:             raise RuntimeError("fallo de hashing")
66:         def verificar(self, password, password_hash):
67:             return False
68:     repo = MemoryUserRepository()
69:     servicio = RegistroService(repo, HashFalla())
70:     with pytest.raises(RuntimeError):
71:         servicio.registrar("Cliente", "cliente@ejemplo.com", PASSWORD, PASSWORD)
72:     assert repo.buscar_por_correo("cliente@ejemplo.com") is None
```

## tests/test_registration.py::test_fallo_repositorio_no_expone_excepcion

```python
75: def test_fallo_repositorio_no_expone_excepcion(cliente):
76:     class RepoFalla(MemoryUserRepository):
77:         def crear_cuenta(self, usuario, credencial):
78:             raise RuntimeError("detalle interno sensible")
79:     repo = RepoFalla()
80:     cliente.app.state.registro_service = RegistroService(repo, Argon2PasswordHasher())
81:     r = cliente.post("/auth/register", json=datos())
82:     assert r.status_code == 503
83:     assert "detalle interno sensible" not in r.text
```

## tests/test_registration.py::test_colision_en_guardado_transformada_a_conflicto

```python
86: def test_colision_en_guardado_transformada_a_conflicto(cliente):
87:     class RepoColision(MemoryUserRepository):
88:         def crear_cuenta(self, usuario, credencial):
89:             raise ValueError("Cuenta duplicada")
90:     cliente.app.state.registro_service = RegistroService(RepoColision(), Argon2PasswordHasher())
91:     assert cliente.post("/auth/register", json=datos()).status_code == 409
```

## tests/test_sessions.py::test_ruta_protegida_sin_cookie

```python
28: def test_ruta_protegida_sin_cookie(cliente):
29:     assert cliente.get('/auth/session').status_code == 401
30:     assert cliente.get('/auth/csrf').status_code == 401
```

## tests/test_sessions.py::test_sesion_vigente

```python
33: def test_sesion_vigente(cliente):
34:     token = entrar(cliente)
35:     r = cliente.get('/auth/session')
36:     assert r.status_code == 200 and r.json()['estado_sesion'] == 'VIGENTE'
37:     assert cliente.app.state.sesiones.buscar(token) is not None
```

## tests/test_sessions.py::test_actualizar_actividad_sin_extender_limite_absoluto

```python
40: def test_actualizar_actividad_sin_extender_limite_absoluto(cliente):
41:     token = entrar(cliente)
42:     repo = cliente.app.state.sesiones
43:     previa = repo.buscar(token)
44:     cliente.get('/auth/session')
45:     nueva = repo.buscar(token)
46:     assert nueva.expira_en == previa.expira_en
47:     assert nueva.ultima_actividad_en >= previa.ultima_actividad_en
```

## tests/test_sessions.py::test_inactividad_de_30_minutos

```python
50: def test_inactividad_de_30_minutos(cliente):
51:     token = entrar(cliente)
52:     repo = cliente.app.state.sesiones
53:     sesion = repo.buscar(token)
54:     repo.guardar(replace(sesion, ultima_actividad_en=sesion.creado_en))
55:     with pytest.raises(SesionNoVigente):
56:         cliente.app.state.session_service.autenticar(token, sesion.creado_en + timedelta(minutes=30))
57:     assert repo.buscar(token) is None
```

## tests/test_sessions.py::test_limite_absoluto_ocho_horas

```python
60: def test_limite_absoluto_ocho_horas(cliente):
61:     token = entrar(cliente)
62:     repo = cliente.app.state.sesiones
63:     sesion = repo.buscar(token)
64:     repo.guardar(replace(sesion, ultima_actividad_en=sesion.expira_en))
65:     with pytest.raises(SesionNoVigente):
66:         cliente.app.state.session_service.autenticar(token, sesion.expira_en)
67:     assert repo.buscar(token) is None
```

## tests/test_sessions.py::test_logout_requiere_csrf

```python
70: def test_logout_requiere_csrf(cliente):
71:     token = entrar(cliente)
72:     assert cliente.post('/auth/logout').status_code == 403
73:     assert cliente.app.state.sesiones.buscar(token) is not None
74:     assert cliente.post('/auth/logout', headers={'x-csrf-token': 'incorrecto'}).status_code == 403
```

## tests/test_sessions.py::test_logout_invalida_token_y_cookie

```python
77: def test_logout_invalida_token_y_cookie(cliente):
78:     token = entrar(cliente)
79:     csrf = cliente.get('/auth/csrf').json()['csrf_token']
80:     r = cliente.post('/auth/logout', headers={'x-csrf-token': csrf})
81:     assert r.status_code == 200
82:     assert r.json() == {'mensaje': 'Sesión cerrada'}
83:     assert 'Max-Age=0' in r.headers['set-cookie']
84:     assert cliente.app.state.sesiones.buscar(token) is None
85:     assert cliente.get('/auth/session').status_code == 401
86:     cliente.cookies.set('continuity_session', token, path='/auth')
87:     assert cliente.get('/auth/session').status_code == 401
```

## tests/test_sessions.py::test_csrf_es_especifico_para_cada_sesion

```python
90: def test_csrf_es_especifico_para_cada_sesion(cliente):
91:     t1 = entrar(cliente)
92:     csrf1 = cliente.get('/auth/csrf').json()['csrf_token']
93:     t2 = entrar(cliente)
94:     csrf2 = cliente.get('/auth/csrf').json()['csrf_token']
95:     assert csrf1 != csrf2 and t1 != t2
96:     assert cliente.post('/auth/logout', headers={'x-csrf-token': csrf1}).status_code == 403
97:     assert cliente.post('/auth/logout', headers={'x-csrf-token': csrf2}).status_code == 200
```

## tests/test_sessions.py::test_origen_cruzado_rechazado

```python
104: def test_origen_cruzado_rechazado(cliente, endpoint, body):
105:     r = cliente.post(endpoint, json=body, headers={'origin': 'https://externo.example'})
106:     assert r.status_code == 403
107:     r = cliente.post(endpoint, json=body, headers={'sec-fetch-site': 'cross-site'})
108:     assert r.status_code == 403
```

## tests/test_sessions.py::test_logout_origen_cruzado_rechazado

```python
111: def test_logout_origen_cruzado_rechazado(cliente):
112:     entrar(cliente)
113:     csrf = cliente.get('/auth/csrf').json()['csrf_token']
114:     assert cliente.post('/auth/logout', headers={
115:         'x-csrf-token': csrf, 'origin': 'https://externo.example'}).status_code == 403
```

## tests/test_sessions.py::test_sesion_ausente_no_se_reactiva

```python
118: def test_sesion_ausente_no_se_reactiva(cliente):
119:     assert cliente.app.state.session_service._sesiones.buscar('desconocida') is None
120:     with pytest.raises(SesionNoVigente):
121:         cliente.app.state.session_service.autenticar('desconocida', datetime.now(timezone.utc))
```
