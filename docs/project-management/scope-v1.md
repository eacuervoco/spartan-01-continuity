# ContinuitY Platform — Scope v1.0

**Proyecto:** Spartan #01  
**Producto:** ContinuitY Platform  
**Versión:** 0.1  
**Estado:** Baseline aprobada  
**Marco de gestión:** Scrum  
**Horizonte:** 12 semanas  

---

## 1. Objetivo del alcance v1.0

La versión 1.0 de ContinuitY Platform debe demostrar que es posible apoyar
una decisión básica de modernización tecnológica de una PYME mediante
información estructurada, evidencia técnica, conocimiento documentado y
comparación de alternativas.

La v1.0 no pretende resolver todos los escenarios posibles de modernización
empresarial.

Su propósito es entregar un producto funcional, demostrable, documentado y
suficientemente completo para validar el concepto de ContinuitY.

---

## 2. Capacidades incluidas en v1.0

ContinuitY v1.0 incluirá las siguientes capacidades.

### 2.1 Diagnóstico tecnológico

El sistema permitirá registrar información básica de una empresa, sus
recursos tecnológicos disponibles, su estado y necesidades identificadas.

Relacionado con:

- RF-01.

---

### 2.2 Recolección de evidencia técnica

ContinuitY permitirá obtener evidencia objetiva de los recursos tecnológicos
evaluados mediante procedimientos compatibles inicialmente con Windows y
Linux.

El cliente ejecutará localmente los comandos suministrados y el procedimiento
generará automáticamente:

`ContinuitY_assessment.txt`

El archivo podrá contener información relacionada con:

- sistema operativo;
- hostname;
- arquitectura;
- CPU;
- memoria;
- almacenamiento;
- filesystem;
- interfaces de red;
- metadata del assessment.

El cliente podrá revisar el archivo antes de entregarlo.

ContinuitY preservará la evidencia original y podrá extraer posteriormente
información estructurada para utilizarla dentro del diagnóstico.

Relacionado con:

- RF-02;
- RNF-02;
- RNF-03;
- RNF-05.

---

### 2.3 Gestión de documentación técnica

El sistema permitirá registrar, organizar y consultar documentación técnica.

Los documentos podrán clasificarse mediante información como:

- fabricante;
- modelo;
- versión;
- tipo de documento.

Relacionado con:

- RF-03.

---

### 2.4 Consulta asistida mediante IA y RAG

La plataforma incorporará una capacidad de consulta sobre documentación
técnica utilizando IA y un mecanismo RAG.

Las respuestas deberán conservar referencia a la evidencia documental
utilizada.

Relacionado con:

- RF-04;
- RNF-02.

---

### 2.5 Evaluación de alternativas

El sistema permitirá registrar resultados obtenidos al evaluar alternativas
de ejecución:

- Local;
- Cloud;
- Híbrida.

Las evaluaciones podrán considerar:

- tiempos;
- consumo de recursos;
- calidad;
- costos estimados;
- observaciones.

Relacionado con:

- RF-05.

---

### 2.6 Recomendación de modernización

La plataforma podrá producir una recomendación basada en:

- diagnóstico;
- evidencia técnica;
- pruebas realizadas;
- evidencia disponible;
- resultados comparativos.

Una recomendación válida podrá concluir que una alternativa tecnológica no
es adecuada.

La recomendación no deberá asumir que la sustitución de infraestructura
existente es siempre necesaria.

Relacionado con:

- RF-06.

---

## 3. Capacidades técnicas incluidas

La v1.0 podrá incorporar progresivamente:

- Python;
- FastAPI;
- Pydantic;
- PostgreSQL;
- filesystem o almacenamiento equivalente para evidencia;
- Docker;
- Docker Compose;
- pruebas automatizadas;
- logging;
- healthchecks;
- CI;
- IA local;
- RAG;
- tool calling;
- un agente acotado;
- experimentación equivalente en AWS cuando aporte valor.

Estas tecnologías no constituyen por sí mismas alcance funcional.

Solo se incorporarán cuando soporten un requisito, reduzcan un riesgo o
permitan demostrar una mejora medible.

---

## 4. Requisitos no funcionales considerados

### RNF-01 — Desempeño

Las operaciones principales de registro, consulta, recuperación y
procesamiento deberán tener un desempeño adecuado para el escenario de
prueba.

Los umbrales cuantitativos deberán establecerse cuando exista una baseline
operacional verificable.

### RNF-02 — Trazabilidad

Las respuestas basadas en IA y las recomendaciones no deberán presentarse
como sustentadas si no existe evidencia suficiente.

La solución deberá permitir diferenciar cuando corresponda entre:

- evidencia original;
- datos procesados;
- interpretación;
- respuesta generada;
- recomendación.

### RNF-03 — Seguridad

La información deberá procesarse solamente mediante alternativas
autorizadas.

No se almacenarán credenciales, secretos ni datos sensibles dentro del
repositorio.

Los procedimientos de recolección deberán aplicar minimización de datos y
el cliente podrá revisar `ContinuitY_assessment.txt` antes de entregarlo.

### RNF-04 — Usabilidad

La solución deberá poder ser utilizada por usuarios sin conocimiento
especializado en inteligencia artificial.

Los procedimientos de assessment deberán presentar instrucciones
comprensibles y minimizar pasos manuales innecesarios.

### RNF-05 — Compatibilidad y uso eficiente de recursos

Antes de recomendar reemplazo de infraestructura, deberán evaluarse los
recursos existentes.

La plataforma permitirá considerar alternativas:

- Local;
- Cloud;
- Híbrida.

La evidencia obtenida del hardware existente deberá formar parte de la
evaluación.

---

## 5. Caso de estudio de v1.0

La validación inicial se realizará utilizando el caso ficticio:

**TecniRed Sabana S.A.S.**

El caso de estudio servirá para validar:

- diagnóstico tecnológico;
- recolección de evidencia técnica;
- organización documental;
- consulta de información;
- evaluación de alternativas;
- generación de evidencia;
- recomendación de modernización.

TecniRed Sabana S.A.S. no forma parte de la identidad permanente del
producto.

---

## 6. Fuera del alcance de v1.0

Quedan explícitamente fuera de Spartan #01 v1.0:

- plataforma SaaS multiempresa;
- sistema multiusuario avanzado;
- autenticación empresarial;
- autorización mediante roles complejos;
- facturación;
- pagos;
- integración con sistemas ERP;
- integración con CRM;
- marketplace;
- aplicación móvil nativa;
- alta disponibilidad empresarial;
- clustering;
- escalamiento automático avanzado;
- soporte de múltiples proveedores cloud;
- agente autónomo con capacidad de ejecutar cambios críticos;
- automatización de decisiones empresariales sin intervención humana;
- fine-tuning de modelos;
- entrenamiento de modelos propios;
- infraestructura de GPU dedicada;
- migración completa de infraestructura de clientes;
- monitoreo en tiempo real de infraestructura empresarial;
- plataforma NOC completa;
- soporte productivo 24x7;
- acceso remoto obligatorio a equipos del cliente;
- agente residente obligatorio en equipos del cliente.

Estas capacidades podrán evaluarse posteriormente para versiones futuras.

---

## 7. Candidatos para v2

Podrán formar parte de una evolución posterior:

- multiempresa;
- autenticación y autorización;
- perfiles de usuario;
- inventario tecnológico avanzado;
- workflows de evaluación;
- dashboards ejecutivos;
- múltiples agentes especializados;
- MCP;
- integración con herramientas externas;
- monitoreo automatizado;
- recomendaciones continuas;
- múltiples proveedores cloud;
- capacidades SaaS;
- analítica histórica;
- collectors automatizados;
- agente o CLI de recolección cuando exista justificación operativa.

La inclusión de estos elementos en una versión futura requerirá nueva
priorización y validación de negocio.

---

## 8. Restricciones de Spartan #01

La ejecución de v1.0 está condicionada por:

- horizonte máximo de 12 semanas;
- uso de Scrum como único marco de gestión;
- arquitectura evolutiva;
- infraestructura disponible en SpartanLab;
- AWS utilizado como laboratorio y entorno comparativo;
- prioridad sobre soluciones simples y mantenibles;
- uso de información sintética o pública;
- control de costos;
- protección de secretos y credenciales;
- preservación de la evidencia técnica original;
- ausencia de acceso remoto obligatorio al entorno del cliente.

---

## 9. Criterio de control de alcance

Una nueva funcionalidad podrá incorporarse a v1.0 solamente si:

1. soporta directamente un requisito aprobado;
2. reduce un riesgo relevante;
3. es necesaria para cumplir el Product Goal;
4. puede implementarse sin comprometer el horizonte de 12 semanas.

En caso contrario deberá incorporarse al Product Backlog para evaluación
posterior.

---

## 10. Definición de éxito de v1.0

ContinuitY v1.0 será considerada exitosa cuando exista un sistema funcional
capaz de demostrar el siguiente flujo:

Empresa  
→ diagnóstico  
→ evidencia técnica  
→ recursos  
→ documentación  
→ consulta  
→ evaluación  
→ comparación  
→ recomendación

y dicho flujo pueda ser demostrado mediante:

- código;
- pruebas;
- documentación;
- evidencia técnica;
- trazabilidad.

---

## 11. Trazabilidad principal del alcance

| Capacidad | Requisito |
|---|---|
| Diagnóstico tecnológico | RF-01 |
| Recolección de evidencia técnica | RF-02 |
| Gestión documental | RF-03 |
| Consulta mediante IA y RAG | RF-04 |
| Evaluación de alternativas | RF-05 |
| Recomendación de modernización | RF-06 |