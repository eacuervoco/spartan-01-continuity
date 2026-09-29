# ContinuitY Platform
## F0.6 — Matriz de Trazabilidad Inicial

**Proyecto:** Spartan #01  
**Producto:** ContinuitY Platform  
**Fase:** F0 — Project Foundation  
**Bloque:** F0.6 — Trazabilidad inicial  
**Versión:** 1.0  
**Estado:** Baseline inicial  
**Fecha:** Septiembre 2026  

---

# 1. Propósito

Esta matriz establece la trazabilidad inicial entre los problemas
identificados en el caso de estudio, los requisitos definidos en F0.5,
los conceptos de modelo que deberán representarlos y la evidencia esperada.

La relación utilizada es:

Problema -> Requisito -> Modelo -> Evidencia

Esta matriz no define todavía clases Python, tablas de base de datos,
endpoints ni componentes de arquitectura.

---

# 2. Problemas identificados

## P-01 — Falta de diagnóstico tecnológico estructurado

La organización no dispone de una evaluación estructurada que permita
conocer sus recursos tecnológicos, estado y necesidades antes de tomar
decisiones de modernización.

---

## P-02 — Falta de evidencia objetiva de hardware y sistema operativo

La información sobre los equipos puede depender de registros manuales,
suposiciones o conocimiento informal.

Se requiere obtener evidencia técnica directamente desde los sistemas
evaluados.

---

## P-03 — Documentación técnica dispersa

La documentación técnica se encuentra distribuida entre diferentes
ubicaciones y medios, dificultando localizar información correspondiente
a fabricantes, modelos y versiones específicas.

---

## P-04 — Dificultad para recuperar conocimiento técnico

Aunque exista documentación, localizar manualmente información relevante
puede consumir tiempo y dificultar la resolución de consultas técnicas.

---

## P-05 — Falta de comparación objetiva entre alternativas

La organización no dispone de un mecanismo estructurado para registrar y
comparar resultados de soluciones Local, Cloud o Híbridas.

---

## P-06 — Decisiones de modernización sin suficiente evidencia

Sin diagnóstico, evidencia técnica y resultados comparables, una decisión
de modernización puede basarse en percepción o asumir innecesariamente que
los recursos existentes deben reemplazarse.

---

# 3. Matriz principal de trazabilidad

| Problema | Requisito | Modelo / concepto relacionado | Evidencia esperada |
|---|---|---|---|
| P-01 Falta de diagnóstico estructurado | RF-01 Diagnóstico tecnológico | Company, TechnologyAssessment, TechnologyResource, TechnologyNeed | Diagnóstico registrado con empresa, recursos, estados y necesidades |
| P-02 Falta de evidencia objetiva de HW/SO | RF-02 Recolección de evidencia técnica | TechnicalEvidence, HardwareSnapshot | `ContinuitY_assessment.txt` original + información extraída |
| P-03 Documentación técnica dispersa | RF-03 Gestión documental | TechnicalDocument | Documento registrado y consultable mediante metadatos |
| P-04 Dificultad para recuperar conocimiento | RF-04 Consulta documental IA + RAG | TechnicalDocument + concepto futuro de consulta/recuperación | Consulta + evidencia documental recuperada + respuesta referenciada |
| P-05 Falta de comparación de alternativas | RF-05 Evaluación de alternativas | TechnologyEvaluation | Registro de resultados Local, Cloud o Híbridos |
| P-06 Decisiones sin evidencia suficiente | RF-06 Recomendación de modernización | ModernizationRecommendation | Recomendación vinculada con diagnóstico y evaluaciones |

---

# 4. Trazabilidad de requisitos no funcionales

| Requisito | Riesgo / necesidad | Evidencia esperada |
|---|---|---|
| RNF-01 Desempeño | Evitar operaciones con tiempos inadecuados y definir métricas únicamente con baseline real | Mediciones y pruebas de desempeño cuando exista implementación |
| RNF-02 Trazabilidad | Evitar presentar inferencias o respuestas de IA como hechos documentados | Relación verificable entre evidencia original, datos procesados y resultado |
| RNF-03 Seguridad | Evitar exposición de secretos o información no requerida | Procedimientos de recolección minimizados, revisión del archivo por el cliente y ausencia de secretos |
| RNF-04 Usabilidad | Permitir uso sin conocimientos especializados en IA | Instrucciones comprensibles y procedimientos con pocos pasos |
| RNF-05 Compatibilidad y eficiencia | Evitar recomendar sustitución de recursos sin evaluarlos previamente | Evidencia de HW existente y comparación Local / Cloud / Híbrida |

---

# 5. Trazabilidad específica de RF-02

RF-02 requiere una trazabilidad adicional debido a que la evidencia técnica
será utilizada posteriormente por otros procesos del producto.

Flujo:

Recurso tecnológico
    |
    v
Procedimiento de recolección
    |
    v
Comandos Windows / Linux
    |
    v
ContinuitY_assessment.txt
    |
    v
Raw Evidence
    |
    v
Normalized Data
    |
    v
Technology Assessment
    |
    v
Evaluación / recomendación

## Evidencia primaria

El archivo:

`ContinuitY_assessment.txt`

representa la evidencia técnica original entregada por el cliente.

## Datos derivados

ContinuitY podrá interpretar posteriormente el archivo para obtener datos
estructurados de:

- sistema operativo;
- arquitectura;
- CPU;
- memoria;
- almacenamiento;
- filesystem;
- red;
- metadata del assessment.

## Regla de trazabilidad

Los datos estructurados deberán mantener relación con la evidencia original
de la cual fueron obtenidos.

Una interpretación o recomendación no deberá sustituir ni modificar la
evidencia original.

---

# 6. Dependencias funcionales

RF-01
Diagnóstico tecnológico
    |
    +---- RF-02
    |     Evidencia técnica
    |
    +---- RF-05
          Evaluación de alternativas
             |
             v
           RF-06
     Recomendación

RF-03
Gestión documental
    |
    v
RF-04
Consulta IA + RAG

Relación principal:

RF-01 + RF-02 + RF-05 -> RF-06

Relación documental:

RF-03 -> RF-04

---

# 7. Conceptos candidatos para modelado UML

A partir de los requisitos y de esta matriz se identifican inicialmente:

- Company
- TechnologyAssessment
- TechnologyResource
- TechnologyNeed
- TechnicalEvidence
- HardwareSnapshot
- TechnicalDocument
- TechnologyEvaluation
- ModernizationRecommendation

Estos elementos constituyen candidatos para F0.7 UML.

Su presencia en esta matriz no implica que todos deban convertirse
directamente en clases de software.

F0.7 deberá determinar cuáles representan realmente elementos del dominio
y qué relaciones existen entre ellos.

---

# 8. Cobertura

## Requisitos funcionales

- RF-01 -> P-01
- RF-02 -> P-02
- RF-03 -> P-03
- RF-04 -> P-04
- RF-05 -> P-05
- RF-06 -> P-06

Cobertura funcional:

6 / 6 requisitos funcionales trazados.

## Requisitos no funcionales

- RNF-01 -> Evidencia futura de desempeño.
- RNF-02 -> Trazabilidad transversal.
- RNF-03 -> Seguridad transversal.
- RNF-04 -> Usabilidad transversal.
- RNF-05 -> Compatibilidad y eficiencia transversal.

Cobertura no funcional:

5 / 5 requisitos no funcionales trazados.

---

# 9. Resultado F0.6

La baseline inicial establece trazabilidad entre:

- 6 problemas de negocio;
- 6 requisitos funcionales;
- 5 requisitos no funcionales;
- conceptos preliminares de dominio;
- evidencia esperada.

Todos los requisitos definidos en F0.5 disponen de una relación inicial
con un problema o necesidad identificada.

---

# 10. Estado

**F0.6 — Trazabilidad inicial: DONE**

Entregable:

`docs/requirements/traceability-matrix.md`

Siguiente bloque:

**F0.7 — UML v0**

Objetivo:

Representar el dominio de ContinuitY a partir de los requisitos y de la
trazabilidad definida, evitando introducir decisiones de arquitectura
prematuras.