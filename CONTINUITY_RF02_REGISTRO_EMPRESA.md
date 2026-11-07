# ContinuitY — RF02: Registro de empresa

**Versión:** 1.0  
**Estado:** Especificación funcional para implementación  
**Objetivo:** MVP, sin sobreingeniería  
**Dependencia:** RF01 (registro, inicio de sesión y sesión vigente)

## 1. Propósito

Permitir que un usuario autenticado registre **una empresa** en ContinuitY y consulte sus datos posteriormente. Este registro habilitará, en requisitos futuros, la asociación del inventario tecnológico y los diagnósticos con esa empresa.

**Criterio de éxito:** un usuario con sesión vigente completa un formulario sencillo, guarda la empresa en PostgreSQL, recibe confirmación y puede volver a consultar la empresa registrada después de iniciar una nueva sesión.

## 2. Alcance exacto

**RF02 incluye:**
1. Mostrar un formulario de registro de empresa a un usuario autenticado.
2. Validar los datos esenciales del formulario.
3. Guardar la empresa en PostgreSQL y asociarla al identificador del usuario autenticado de RF01.
4. Impedir que el mismo usuario registre una segunda empresa en este MVP.
5. Consultar la empresa asociada al usuario y mostrar sus datos.
6. Mostrar mensajes comprensibles en casos de éxito o error.

**RF02 no incluye:** invitaciones de usuarios; varios usuarios por empresa; múltiples empresas por cuenta; roles empresariales; sucursales; carga de documentos; verificación de NIT contra fuentes externas; integraciones de terceros; inventario de activos; diagnóstico; IA; edición o eliminación de empresa; panel de administración; recuperación de sesión o cambios en RF01.

> La plataforma puede contener muchas empresas, pero **cada usuario registra una sola empresa** durante este MVP. No equivale a implementar organizaciones multiusuario.

## 3. Actor y precondiciones

- **Actor:** usuario registrado con sesión vigente de RF01.
- El backend obtiene el identificador del usuario **de la autenticación existente**, nunca del cuerpo enviado por el navegador.
- Si no hay una sesión válida, se deniega el acceso a las operaciones de RF02 utilizando el mecanismo que ya exista en RF01.

## 4. Datos de empresa

| Campo | Obligatorio | Reglas mínimas |
|---|---|---|
| Nombre de empresa / razón social | Sí | Texto no vacío después de quitar espacios iniciales/finales; máximo 150 caracteres. |
| NIT | No | Texto, máximo 20 caracteres; no consultar DIAN ni implementar dígito de verificación. |
| Ciudad / municipio | Sí | Texto no vacío; máximo 100 caracteres. |
| Sector económico | No | Texto libre, máximo 100 caracteres; sin catálogo externo. |

**Generados por el sistema:** `id` de empresa (UUID), `usuario_id` (UUID recuperado de RF01), `creado_en` (fecha/hora UTC).

No solicitar dirección, teléfono, representante legal, número de empleados ni infraestructura tecnológica en RF02. Si se requieren en otro flujo, definirlos en un requisito posterior.

## 5. Flujo principal

1. El usuario inicia sesión mediante RF01.
2. Abre la sección «Registrar empresa».
3. Si ya tiene empresa, ve sus datos y no se presenta un segundo formulario de registro.
4. Si no tiene empresa, completa **Nombre de empresa** y **Ciudad / municipio**; puede agregar NIT y sector.
5. El frontend envía los datos al backend.
6. El backend verifica la sesión, valida los campos y verifica que el usuario no tenga empresa.
7. El backend persiste el registro en PostgreSQL, asociado al usuario autenticado.
8. El sistema muestra «Empresa registrada correctamente» y permite consultar sus datos.

## 6. Casos alternos y errores

| Situación | Comportamiento esperado |
|---|---|
| Sin autenticación o sesión expirada | Rechazar con HTTP 401 según la integración real con RF01 y dirigir al inicio de sesión desde la interfaz. |
| Nombre o ciudad vacíos / formato incorrecto | HTTP 422; mostrar validación legible sin guardar datos. |
| El usuario ya tiene empresa | HTTP 409 al intentar registrar nuevamente; consultar y mostrar la empresa existente. |
| Error de persistencia | Responder con error controlado HTTP 500; no mostrar detalles internos ni credenciales. |

La duplicidad se controla también con una **restricción UNIQUE en `usuario_id` en la base de datos**, evitando carreras entre solicitudes simultáneas. No exigir NIT único: es opcional y la cuenta empresarial no se valida externamente en este MVP.

## 7. Interfaz de usuario

Crear una vista simple consistente con la estética actual de ContinuitY:

- Formulario de cuatro campos, únicamente dos obligatorios.
- Botón **«Registrar empresa»**; deshabilitarlo durante el envío para evitar dobles clics.
- Mensajes claros y visibles para error, éxito y sesión expirada.
- Si la empresa ya existe, mostrar una ficha de solo lectura con los datos guardados.
- HTML semántico y accesible, `lang="es"`, codificación UTF-8, exactamente un `<h1>` por página, etiquetas asociadas a entradas, diseño adaptable a móvil.
- Separar HTML, CSS y JavaScript en archivos distintos y **reutilizar** estilos, componentes y mecanismos existentes de RF01 cuando sea posible.
- No incorporar frameworks frontend, asistentes paso a paso, gráficos ni dependencias nuevas salvo necesidad justificada.
- No crear un dashboard general si aún no existe; basta la confirmación y la consulta de la empresa.

## 8. Contrato de API propuesto

**Adaptar las rutas a las convenciones existentes del repositorio; no duplicar middleware ni autenticación.**

| Método | Ruta sugerida | Función | Respuesta esperada |
|---|---|---|---|
| `POST` | `/companies` | Registrar empresa para usuario autenticado | `201 Created` + datos públicos de empresa |
| `GET` | `/companies/me` | Consultar empresa del usuario autenticado | `200 OK` + datos; `404` si no existe |

**Solicitud POST (ejemplo):**

```json
{
  "nombre": "TecniRed Sabana",
  "nit": "900123456-7",
  "ciudad": "Bogotá",
  "sector": "Servicios tecnológicos"
}
```

**Respuesta exitosa (ejemplo ilustrativo):**

```json
{
  "id": "2c966bd2-b7e8-4f79-820d-04b1512362cf",
  "nombre": "TecniRed Sabana",
  "nit": "900123456-7",
  "ciudad": "Bogotá",
  "sector": "Servicios tecnológicos",
  "creado_en": "2026-11-06T15:00:00Z"
}
```

La respuesta **no** expone credenciales, tokens ni datos privados del usuario. El identificador del propietario se determina internamente.

## 9. Persistencia y diseño técnico

Mantener el monolito existente de tres capas:

1. **Dominio:** entidad `Empresa` y reglas mínimas de registro.
2. **Infraestructura:** repositorio PostgreSQL para guardar y consultar por usuario autenticado.
3. **API:** rutas, validación de entrada/salida e integración con la sesión de RF01.

Usar Python, FastAPI, PostgreSQL y las herramientas ya presentes. Preferir POO sencilla y objetos de dominio acordes con el proyecto, sin introducir patrones o servicios innecesarios.

**Modelo lógico mínimo:** `empresas(id UUID PK, usuario_id UUID NOT NULL UNIQUE, nombre VARCHAR(150) NOT NULL, nit VARCHAR(20) NULL, ciudad VARCHAR(100) NOT NULL, sector VARCHAR(100) NULL, creado_en TIMESTAMPTZ NOT NULL)`.

- Incorporar clave foránea `usuario_id` hacia la tabla real de usuarios **solo después de inspeccionar el esquema existente**.
- Definir migración o script versionado de manera coherente con el mecanismo de esquema ya utilizado por RF01. No borrar ni recrear tablas existentes.
- No introducir otra base de datos, ORM, herramienta de migración ni paquetes sin justificación.
- Las operaciones de creación deben ser transaccionales y aprovechar la restricción de unicidad de PostgreSQL.

## 10. Pruebas y aceptación

**Criterios de aceptación (CA):**

- **CA01:** un usuario autenticado sin empresa puede registrar nombre y ciudad válidos.
- **CA02:** NIT y sector son opcionales.
- **CA03:** el registro se guarda en PostgreSQL y permanece tras reiniciar el servicio / nueva sesión.
- **CA04:** la empresa queda asociada al usuario autenticado, no a un `usuario_id` proporcionado por el cliente.
- **CA05:** el usuario autenticado puede consultar únicamente su propia empresa.
- **CA06:** un segundo registro del mismo usuario devuelve 409 sin generar duplicados.
- **CA07:** las peticiones no autenticadas se rechazan.
- **CA08:** las entradas inválidas no generan registros y devuelven errores comprensibles.
- **CA09:** el frontend permite registro y consulta, maneja estados de error y cumple las reglas de accesibilidad y separación de archivos.
- **CA10:** las pruebas existentes de RF01 continúan pasando.

**Pruebas mínimas:** casos felices, opcionales omitidos, validaciones, duplicado, no autenticado, aislamiento entre usuarios y persistencia real en PostgreSQL. Aplicar `pytest` siguiendo la estructura ya creada. No afirmar que la persistencia está validada usando solamente repositorios en memoria.

## 11. Entregables de RF02

1. Implementación backend integrada al proyecto existente.
2. Esquema SQL / migración mínima versionada y no destructiva.
3. Frontend de registro y consulta de empresa.
4. Pruebas automatizadas y evidencia de ejecución.
5. README breve con cómo ejecutar y probar RF02, endpoints y decisiones relevantes.

## 12. Instrucciones de ejecución para Codex

**Primera ejecución — análisis exclusivamente:**

- Leer este documento y solo los archivos imprescindibles para conocer estructura, RF01, autenticación, conexión PostgreSQL, frontend y pruebas.
- No escribir ni modificar archivos; no instalar paquetes; no ejecutar migraciones.
- Identificar discrepancias entre esta especificación y la implementación real.
- Entregar un plan incremental con archivos afectados y pruebas propuestas; esperar aprobación antes de implementar.

**Implementación posterior, previa autorización:**

1. Reutilizar RF01 sin refactorizaciones ajenas al alcance.
2. Implementar dominio, repositorio y API con sus pruebas.
3. Añadir persistencia y validar con PostgreSQL de desarrollo.
4. Implementar formulario y vista de consulta.
5. Ejecutar pruebas RF01 + RF02; mostrar resultados y cambios (`git diff`).

**Política:** menos es más; código claro y mantenible, sin sobreingeniería. No agregar funcionalidades que no estén especificadas. Si surge una decisión que afecte seguridad, esquema actual o alcance, exponerla y solicitar aprobación antes del cambio.
