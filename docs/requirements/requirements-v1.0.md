# ContinuitY Platform
## F0.5 — Requisitos Funcionales y No Funcionales

**Proyecto:** Spartan #01  
**Producto:** ContinuitY Platform  
**Fase:** F0 — Project Foundation  
**Bloque:** F0.5 — Requisitos RF/RNF  
**Versión:** 1.0  
**Estado:** Baseline aprobado  
**Fecha:** Septiembre 2026  

---

# 1. Propósito

Este documento establece la baseline de requisitos funcionales y no
funcionales de ContinuitY Platform v1.0.

Los requisitos definen qué capacidades deberá ofrecer el producto y bajo qué
restricciones deberá operar.

Este documento no define todavía:

- arquitectura de software;
- tecnologías de persistencia;
- frameworks;
- APIs;
- modelos de inteligencia artificial;
- proveedores cloud;
- implementación de agentes;
- mecanismos específicos de despliegue.

Estas decisiones serán desarrolladas en los bloques y Sprints
correspondientes.

---

# 2. Contexto del producto

ContinuitY Platform está orientada a apoyar procesos de modernización y
continuidad tecnológica en pequeñas y medianas empresas.

La plataforma busca permitir que una organización:

1. conozca su situación tecnológica;
2. identifique los recursos tecnológicos disponibles;
3. obtenga evidencia objetiva de dichos recursos;
4. organice su documentación técnica;
5. consulte conocimiento basado en evidencia;
6. evalúe alternativas tecnológicas;
7. compare opciones Local, Cloud o Híbridas;
8. produzca información útil para tomar decisiones de modernización.

La incorporación de IA deberá responder a una necesidad concreta y producir
una mejora demostrable.

---

# 3. Flujo funcional de alto nivel

Empresa
    |
    v
RF-01 Diagnóstico tecnológico
    |
    v
RF-02 Recolección de evidencia técnica
    |
    v
RF-03 Gestión documental
    |
    v
RF-04 Consulta mediante IA + RAG
    |
    v
RF-05 Evaluación de alternativas
    |
    v
RF-06 Recomendación de modernización

Los requisitos no funcionales RNF-01 a RNF-05 aplican transversalmente a
estas capacidades.

---

# 4. Requisitos funcionales

## RF-01 — Diagnóstico tecnológico

### Descripción

El sistema deberá permitir registrar, consultar y actualizar un diagnóstico
tecnológico de una empresa, incluyendo información general, recursos
tecnológicos disponibles, estado de dichos recursos, necesidades
identificadas y observaciones relevantes para posteriores decisiones de
modernización.

### Información mínima

#### Empresa

- identificador;
- nombre;
- actividad empresarial;
- ubicación general.

#### Diagnóstico

- identificador;
- empresa asociada;
- fecha;
- responsable;
- resumen;
- observaciones.

#### Recursos tecnológicos

- identificador;
- tipo de recurso;
- fabricante cuando aplique;
- modelo cuando aplique;
- descripción;
- estado;
- observaciones.

#### Necesidades

- descripción;
- prioridad;
- observaciones.

### Estados iniciales de recurso

- OPERATIONAL;
- LIMITED;
- OBSOLETE;
- OUT_OF_SERVICE;
- PENDING_EVALUATION.

### Prioridad de necesidades

- LOW;
- MEDIUM;
- HIGH;
- CRITICAL.

### Criterios de aceptación

**RF01-CA01.** El sistema permite registrar una empresa objeto de evaluación.

**RF01-CA02.** El sistema permite crear un diagnóstico asociado a una
empresa.

**RF01-CA03.** El diagnóstico registra fecha y responsable de la evaluación.

**RF01-CA04.** Se puede registrar uno o más recursos tecnológicos dentro del
diagnóstico.

**RF01-CA05.** Cada recurso puede clasificarse por tipo y estado.

**RF01-CA06.** Fabricante y modelo pueden registrarse cuando sean aplicables.

**RF01-CA07.** Se pueden registrar necesidades tecnológicas detectadas.

**RF01-CA08.** Cada necesidad puede tener una prioridad.

**RF01-CA09.** El diagnóstico completo puede recuperarse posteriormente.

**RF01-CA10.** La información del diagnóstico puede actualizarse.

**RF01-CA11.** Un diagnóstico puede existir sin contener todavía una
recomendación de modernización.

### Regla de negocio

**RF01-BR01.**

Un diagnóstico tecnológico describe el estado observado de la empresa y sus
recursos, pero no constituye por sí mismo una recomendación de
modernización.

---

# RF-02 — Recolección de evidencia técnica de recursos

## Descripción

El sistema deberá proporcionar procedimientos de recolección compatibles
con los sistemas operativos soportados, permitiendo que el cliente ejecute
localmente un conjunto controlado de comandos que genere automáticamente un
archivo estandarizado denominado:

`ContinuitY_assessment.txt`

El archivo deberá contener evidencia técnica del hardware y sistema
operativo del recurso evaluado y podrá ser posteriormente recibido,
conservado y procesado por ContinuitY.

## Principio operacional

ContinuitY no requerirá inicialmente acceso remoto al recurso del cliente.

El procedimiento será:

ContinuitY
    |
    v
Entrega instrucciones
    |
    v
Cliente ejecuta comandos localmente
    |
    v
ContinuitY_assessment.txt
    |
    v
Cliente revisa archivo
    |
    v
Entrega evidencia
    |
    v
ContinuitY conserva archivo original
    |
    v
Extracción de datos
    |
    v
Información estructurada
    |
    v
Diagnóstico

## Sistemas operativos iniciales

La versión inicial deberá contemplar:

- Linux;
- Windows.

La arquitectura futura podrá incorporar otros sistemas operativos sin
modificar el propósito funcional del requisito.

## Categorías mínimas de información

Cuando el sistema operativo permita obtenerlas, la evidencia podrá contener:

### Identificación

- hostname;
- sistema operativo;
- versión;
- arquitectura;
- fecha de recolección.

### CPU

- fabricante;
- modelo;
- arquitectura;
- número de núcleos;
- número de hilos cuando esté disponible.

### Memoria

- memoria RAM total;
- memoria utilizada;
- memoria disponible.

### Almacenamiento

- dispositivos disponibles;
- capacidad;
- particiones o volúmenes;
- espacio utilizado;
- espacio disponible.

### Red

- interfaces;
- estado de interfaces;
- información técnica necesaria para el diagnóstico.

Información sensible no necesaria deberá excluirse siempre que sea posible.

## Formato lógico del archivo

El archivo deberá permitir identificar claramente sus diferentes secciones.

Ejemplo:

===== CONTINUITY ASSESSMENT =====

===== METADATA =====

===== HOSTNAME =====

===== SYSTEM =====

===== CPU =====

===== MEMORY =====

===== STORAGE =====

===== FILESYSTEM =====

===== NETWORK =====

===== END ASSESSMENT =====

La estructura exacta podrá evolucionar manteniendo compatibilidad con la
versión del assessment.

## Evidencia original y datos normalizados

ContinuitY diferenciará conceptualmente:

### Raw Evidence

Archivo original entregado por el cliente:

`ContinuitY_assessment.txt`

### Normalized Data

Datos estructurados obtenidos a partir de la evidencia.

Ejemplo conceptual:

- hostname;
- sistema operativo;
- arquitectura;
- CPU;
- memoria;
- almacenamiento;
- red.

### Assessment

Interpretación posterior de los datos obtenidos.

La evidencia, la interpretación y la recomendación representan
responsabilidades diferentes.

## Criterios de aceptación

**RF02-CA01.** ContinuitY proporciona instrucciones diferenciadas según el
sistema operativo soportado.

**RF02-CA02.** El procedimiento puede ejecutarse sin instalar software
especializado de ContinuitY.

**RF02-CA03.** La ejecución genera automáticamente el archivo
`ContinuitY_assessment.txt`.

**RF02-CA04.** El archivo contiene secciones identificables para las
categorías de información recolectadas.

**RF02-CA05.** El archivo conserva las salidas obtenidas directamente del
sistema operativo.

**RF02-CA06.** El cliente puede revisar el archivo antes de entregarlo.

**RF02-CA07.** ContinuitY puede conservar el archivo original recibido sin
alterar su contenido.

**RF02-CA08.** La evidencia puede asociarse con el recurso tecnológico
correspondiente.

**RF02-CA09.** La evidencia puede asociarse con el diagnóstico
correspondiente.

**RF02-CA10.** ContinuitY puede extraer información estructurada del archivo
recibido.

**RF02-CA11.** La recolección obtiene información de sistema operativo, CPU,
memoria y almacenamiento cuando esté disponible.

**RF02-CA12.** Los datos que no puedan obtenerse deberán identificarse como
no disponibles y no serán inferidos o inventados.

**RF02-CA13.** Cada captura deberá conservar información temporal suficiente
para identificar cuándo fue realizada.

**RF02-CA14.** El sistema deberá permitir conservar múltiples assessments
del mismo recurso sin sobrescribir obligatoriamente evidencias anteriores.

### Reglas de negocio

**RF02-BR01.**

Una captura técnica representa el estado observado de un recurso en un
momento determinado y no constituye por sí misma una evaluación de
capacidad, obsolescencia o recomendación de modernización.

**RF02-BR02 — Minimización de datos.**

Los procedimientos de recolección deberán solicitar únicamente información
necesaria para el diagnóstico tecnológico.

Deberá evitarse, cuando sea posible, recopilar:

- contraseñas;
- tokens;
- claves;
- secretos;
- contenido de archivos personales;
- datos empresariales que no sean necesarios;
- información confidencial ajena al diagnóstico.

---

# RF-03 — Gestión de documentación técnica

## Descripción

El sistema deberá permitir registrar, organizar y consultar documentación
técnica, incluyendo manuales, procedimientos y otros documentos relevantes.

La documentación podrá clasificarse utilizando metadatos como:

- fabricante;
- modelo;
- versión;
- tipo documental.

## Criterios de aceptación

**RF03-CA01.** Se puede registrar un documento técnico.

**RF03-CA02.** Un documento puede clasificarse por fabricante.

**RF03-CA03.** Un documento puede asociarse con modelo cuando aplique.

**RF03-CA04.** Un documento puede asociarse con versión cuando aplique.

**RF03-CA05.** Un documento puede clasificarse por tipo.

**RF03-CA06.** La documentación puede consultarse utilizando sus metadatos.

**RF03-CA07.** El sistema conserva una referencia inequívoca al documento.

---

# RF-04 — Consulta documental mediante IA y RAG

## Descripción

El sistema deberá permitir realizar consultas sobre documentación técnica
utilizando mecanismos de IA y Retrieval-Augmented Generation, conservando
referencia a la evidencia documental utilizada para producir las respuestas.

## Criterios de aceptación

**RF04-CA01.** El usuario puede realizar consultas sobre la documentación
disponible.

**RF04-CA02.** El sistema recupera información relacionada con la consulta
antes de producir una respuesta sustentada documentalmente.

**RF04-CA03.** La respuesta conserva referencia a la evidencia utilizada.

**RF04-CA04.** La evidencia puede identificarse independientemente de la
respuesta generada.

**RF04-CA05.** Cuando no exista evidencia suficiente, el sistema no deberá
presentar una respuesta como sustentada documentalmente.

---

# RF-05 — Evaluación de alternativas tecnológicas

## Descripción

El sistema deberá permitir registrar y consultar resultados de pruebas o
evaluaciones realizadas sobre alternativas tecnológicas Local, Cloud o
Híbridas.

Cuando corresponda, las evaluaciones podrán incluir:

- tiempos;
- consumo de recursos;
- calidad;
- costos estimados;
- observaciones.

## Criterios de aceptación

**RF05-CA01.** Se puede registrar una alternativa tecnológica evaluada.

**RF05-CA02.** La alternativa puede clasificarse como Local, Cloud o
Híbrida.

**RF05-CA03.** Pueden registrarse tiempos de ejecución o respuesta cuando
aplique.

**RF05-CA04.** Puede registrarse consumo de recursos cuando aplique.

**RF05-CA05.** Puede registrarse una medida o resultado relacionado con
calidad.

**RF05-CA06.** Puede registrarse costo estimado cuando corresponda.

**RF05-CA07.** Los resultados permanecen disponibles para comparación
posterior.

---

# RF-06 — Recomendación de modernización

## Descripción

El sistema deberá permitir producir una recomendación de modernización
apoyada en la información disponible del diagnóstico y en los resultados de
las evaluaciones realizadas.

Una recomendación válida podrá determinar que una alternativa tecnológica
no es adecuada.

## Criterios de aceptación

**RF06-CA01.** La recomendación utiliza información proveniente del
diagnóstico tecnológico.

**RF06-CA02.** Puede incorporar resultados de alternativas previamente
evaluadas.

**RF06-CA03.** La recomendación identifica la alternativa o estrategia
evaluada.

**RF06-CA04.** La recomendación conserva información suficiente para
comprender la evidencia en la cual se apoya.

**RF06-CA05.** El sistema permite concluir que una alternativa evaluada no
es adecuada.

**RF06-CA06.** El sistema no deberá asumir que la sustitución de
infraestructura existente es siempre necesaria.

---

# 5. Requisitos no funcionales

## RNF-01 — Desempeño

El sistema deberá proporcionar un desempeño adecuado para las operaciones de
registro, consulta, recuperación y procesamiento de información.

Los umbrales cuantitativos deberán establecerse cuando exista una línea base
operacional verificable.

No deberán definirse métricas arbitrarias sin evidencia.

---

# RNF-02 — Trazabilidad de información e IA

Toda respuesta presentada como sustentada documentalmente deberá mantener
una relación verificable con la evidencia utilizada.

La plataforma deberá diferenciar cuando corresponda entre:

- dato original;
- dato procesado;
- interpretación;
- respuesta generada;
- recomendación.

---

# RNF-03 — Seguridad de la información

La información deberá almacenarse y procesarse únicamente mediante
mecanismos y alternativas autorizadas.

El sistema y sus procedimientos deberán evitar exponer o almacenar
innecesariamente:

- credenciales;
- contraseñas;
- secretos;
- tokens;
- información personal;
- información empresarial sensible.

Los archivos de assessment deberán poder ser revisados por el cliente antes
de ser entregados.

---

# RNF-04 — Usabilidad

Las funciones principales deberán poder ser utilizadas por usuarios que no
posean conocimiento especializado en inteligencia artificial.

Los procedimientos de recolección deberán presentar instrucciones
comprensibles y minimizar pasos manuales innecesarios.

---

# RNF-05 — Compatibilidad y eficiencia de recursos

ContinuitY deberá considerar las capacidades de los recursos tecnológicos
existentes antes de recomendar su sustitución.

El sistema deberá permitir considerar alternativas:

- Local;
- Cloud;
- Híbridas.

La disponibilidad de hardware existente deberá formar parte de la evidencia
utilizada para evaluar alternativas de modernización.

---

# 6. Relaciones principales entre requisitos

RF-01
Diagnóstico tecnológico
    |
    +---- RF-02
    |     Evidencia real de recursos
    |
    +---- RF-05
          Evaluación de alternativas

RF-03
Documentación técnica
    |
    v
RF-04
IA + RAG

RF-01 + RF-02 + RF-05
          |
          v
        RF-06
Recomendación de modernización

---

# 7. Conceptos de dominio identificados

Los requisitos permiten identificar preliminarmente los siguientes conceptos:

- Company
- TechnologyAssessment
- TechnologyResource
- TechnologyNeed
- TechnicalEvidence
- HardwareSnapshot
- TechnicalDocument
- TechnologyEvaluation
- ModernizationRecommendation

Estos conceptos no representan todavía clases Python, tablas de base de
datos ni decisiones arquitectónicas definitivas.

Su modelado será desarrollado posteriormente.

---

# 8. Fuera del alcance de F0.5

F0.5 no determina todavía:

- FastAPI;
- PostgreSQL;
- MongoDB;
- S3;
- AWS RDS;
- Ollama;
- modelos LLM específicos;
- modelo de embeddings;
- vector database;
- arquitectura RAG;
- agentes;
- MCP;
- acceso remoto SSH;
- WinRM;
- agente instalado en dispositivos;
- implementación específica de collectors;
- estructura definitiva de APIs.

Estas decisiones deberán justificarse en los bloques y Sprints
correspondientes.

---

# 9. Baseline funcional v1.0

La baseline de F0.5 queda constituida por:

## Requisitos funcionales

- RF-01 — Diagnóstico tecnológico.
- RF-02 — Recolección de evidencia técnica.
- RF-03 — Gestión documental.
- RF-04 — Consulta documental mediante IA y RAG.
- RF-05 — Evaluación de alternativas.
- RF-06 — Recomendación de modernización.

## Requisitos no funcionales

- RNF-01 — Desempeño.
- RNF-02 — Trazabilidad.
- RNF-03 — Seguridad.
- RNF-04 — Usabilidad.
- RNF-05 — Compatibilidad y eficiencia de recursos.

Total:

- 6 requisitos funcionales.
- 5 requisitos no funcionales.
- 11 requisitos principales.

---

# 10. Control de cambios

| Versión | Cambio |
|---------|--------|
| 0.1 | Requisitos iniciales definidos en Roadmap Maestro |
| 1.0 | Refinamiento formal de RF/RNF e incorporación de RF-02 Technical Assessment |

---

# 11. Estado

**F0.5 — Requisitos RF/RNF: DONE**

Baseline:

`requirements-v1.0`

Siguiente bloque:

**F0.6 — Trazabilidad inicial**

Objetivo:

Construir la matriz:

Problema -> Requisito -> Modelo -> Evidencia