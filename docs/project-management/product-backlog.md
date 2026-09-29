# ContinuitY Platform — Product Backlog

**Proyecto:** Spartan #01  
**Producto:** ContinuitY Platform  
**Fase:** F0 — Project Foundation  
**Bloque:** F0.9 — Product Backlog inicial  
**Versión:** 0.1  
**Estado:** Baseline inicial  
**Marco de gestión:** Scrum  
**Horizonte:** 12 semanas

---

## 1. Propósito

Este documento contiene el Product Backlog inicial de ContinuitY Platform.

El backlog transforma los requisitos, la trazabilidad, el modelo UML y la
arquitectura inicial en trabajo ordenado por valor, dependencia y riesgo.

El Product Backlog es dinámico.

Los PBIs podrán refinarse, dividirse, reordenarse o descartarse conforme
aparezca nueva evidencia durante los Sprints.

---

## 2. Product Goal

Construir en un máximo de 12 semanas una versión v1.0 funcional,
documentada, probada y demostrable de ContinuitY Platform que permita
evaluar recursos tecnológicos, obtener evidencia técnica de dichos recursos,
organizar conocimiento técnico y proporcionar información trazable para
apoyar decisiones de modernización de una PYME.

---

## 3. Criterios de priorización

Los PBIs se ordenan considerando:

1. valor para el Product Goal;
2. dependencia funcional;
3. reducción de riesgo técnico;
4. generación de evidencia verificable;
5. aprendizaje necesario para desbloquear trabajo posterior;
6. capacidad real dentro del horizonte de 12 semanas.

Una tecnología no entra al trabajo activo únicamente por interés técnico.

Debe desbloquear un requisito, reducir un riesgo o permitir demostrar una
mejora medible.

---

## 4. Convenciones

### Prioridad

- **P0** — imprescindible para v1.0;
- **P1** — alta prioridad;
- **P2** — importante pero refinable;
- **P3** — candidato posterior.

### Estado inicial

- **Ready for Refinement** — identificado pero requiere refinamiento;
- **Candidate Sprint 1** — candidato inmediato para Sprint 1;
- **Future Sprint** — planificado para un Sprint posterior;
- **Deferred** — fuera del alcance activo actual.

---

## 5. Product Backlog ordenado

| Orden | PBI | Descripción | Requisitos | Prioridad | Dependencias | Candidato |
|---:|---|---|---|---|---|---|
| 1 | PBI-001 | Crear estructura mínima del backend Python y dominio inicial | RF-01 | P0 | F0 completa | Sprint 1 |
| 2 | PBI-002 | Implementar entidad Company | RF-01 | P0 | PBI-001 | Sprint 1 |
| 3 | PBI-003 | Implementar TechnologyAssessment | RF-01 | P0 | PBI-001, PBI-002 | Sprint 1 |
| 4 | PBI-004 | Implementar TechnologyResource y estados | RF-01 | P0 | PBI-003 | Sprint 1 |
| 5 | PBI-005 | Implementar TechnologyNeed y prioridades | RF-01 | P1 | PBI-003 | Sprint 1 |
| 6 | PBI-006 | Exponer API mínima para crear y consultar diagnósticos | RF-01 | P0 | PBI-002..005 | Sprint 1 |
| 7 | PBI-007 | Crear suite inicial de pruebas de dominio y API | RNF-01, RNF-03 | P0 | PBI-001..006 | Sprint 1 |
| 8 | PBI-008 | Definir formato operativo Linux de `ContinuitY_assessment.txt` | RF-02 | P0 | RF-02 baseline | Sprint 1 / 2 |
| 9 | PBI-009 | Definir formato operativo Windows de `ContinuitY_assessment.txt` | RF-02 | P0 | RF-02 baseline | Sprint 1 / 2 |
| 10 | PBI-010 | Implementar importación de evidencia técnica | RF-02 | P0 | PBI-008, PBI-009 | Sprint 2 |
| 11 | PBI-011 | Preservar Raw Evidence sin modificación | RF-02, RNF-02, RNF-03 | P0 | PBI-010 | Sprint 2 |
| 12 | PBI-012 | Implementar parser inicial de Technical Assessment | RF-02 | P0 | PBI-010, PBI-011 | Sprint 2 |
| 13 | PBI-013 | Generar HardwareSnapshot normalizado | RF-02 | P0 | PBI-012 | Sprint 2 |
| 14 | PBI-014 | Incorporar persistencia PostgreSQL | RF-01, RF-02 | P0 | Backend estable | Sprint 2 |
| 15 | PBI-015 | Containerizar backend y persistencia | RNF-05 | P1 | PBI-014 | Sprint 2 |
| 16 | PBI-016 | Implementar pruebas de integración con PostgreSQL | RNF-01 | P1 | PBI-014 | Sprint 2 |
| 17 | PBI-017 | Implementar gestión de metadatos de documentos técnicos | RF-03 | P0 | Persistencia | Sprint 3 |
| 18 | PBI-018 | Registrar y consultar TechnicalDocument | RF-03 | P0 | PBI-017 | Sprint 3 |
| 19 | PBI-019 | Incorporar logging estructurado básico | RNF-01, RNF-03 | P1 | Backend | Sprint 3 |
| 20 | PBI-020 | Implementar healthcheck de aplicación | RNF-01 | P1 | Backend | Sprint 3 |
| 21 | PBI-021 | Crear pipeline CI para ejecutar pruebas | RNF-01 | P1 | Suite de pruebas | Sprint 3 |
| 22 | PBI-022 | Ejecutar comparación inicial SpartanLab vs AWS para una capacidad seleccionada | RNF-05 | P1 | Componente estable | Sprint 3 |
| 23 | PBI-023 | Definir baseline de consulta documental sin IA | RF-03, RF-04 | P0 | PBI-018 | Sprint 4 |
| 24 | PBI-024 | Implementar recuperación de evidencia documental | RF-04, RNF-02 | P0 | PBI-023 | Sprint 4 |
| 25 | PBI-025 | Integrar servicio de IA para generación basada en evidencia | RF-04 | P0 | PBI-024 | Sprint 4 |
| 26 | PBI-026 | Implementar RAG clásico con referencias de evidencia | RF-04, RNF-02 | P0 | PBI-024, PBI-025 | Sprint 4 |
| 27 | PBI-027 | Evaluar calidad del flujo RAG contra baseline | RF-04, RNF-01, RNF-02 | P0 | PBI-026 | Sprint 4 |
| 28 | PBI-028 | Implementar registro de TechnologyEvaluation | RF-05 | P0 | Diagnóstico + persistencia | Sprint 4 / 5 |
| 29 | PBI-029 | Registrar alternativas Local, Cloud e Híbrida | RF-05 | P0 | PBI-028 | Sprint 5 |
| 30 | PBI-030 | Registrar métricas de evaluación: tiempo, recursos, calidad y costo estimado | RF-05 | P0 | PBI-028 | Sprint 5 |
| 31 | PBI-031 | Implementar comparación de alternativas | RF-05 | P0 | PBI-029, PBI-030 | Sprint 5 |
| 32 | PBI-032 | Implementar ModernizationRecommendation | RF-06 | P0 | RF-01, RF-02, RF-05 | Sprint 5 |
| 33 | PBI-033 | Vincular recomendación con evidencia y evaluaciones | RF-06, RNF-02 | P0 | PBI-032 | Sprint 5 |
| 34 | PBI-034 | Permitir resultado “alternativa no adecuada” | RF-06 | P0 | PBI-032 | Sprint 5 |
| 35 | PBI-035 | Identificar una tarea candidata para tool calling | Agentic roadmap | P1 | Backend + RAG estable | Sprint 5 |
| 36 | PBI-036 | Implementar tool calling acotado | Agentic roadmap | P1 | PBI-035 | Sprint 5 |
| 37 | PBI-037 | Incorporar guardrails para tool calling | RNF-03 | P0 | PBI-036 | Sprint 5 |
| 38 | PBI-038 | Evaluar agente acotado contra solución determinista | Agentic roadmap | P1 | PBI-036, PBI-037 | Sprint 5 |
| 39 | PBI-039 | Hardening de seguridad, configuración y secretos | RNF-03 | P0 | Sistema integrado | Semana 12 |
| 40 | PBI-040 | Ejecutar pruebas end-to-end del flujo v1.0 | Todos | P0 | Sistema integrado | Semana 12 |
| 41 | PBI-041 | Actualizar README y documentación final | Todos | P1 | Sistema integrado | Semana 12 |
| 42 | PBI-042 | Documentar comparativa final Local vs AWS | RNF-05 | P1 | Labs ejecutados | Semana 12 |
| 43 | PBI-043 | Preparar demo reproducible de ContinuitY v1.0 | Todos | P0 | PBI-040..042 | Semana 12 |
| 44 | PBI-044 | Preparar case study de portafolio | Portfolio | P1 | v1.0 cerrada | Semana 12 |

---

## 6. Backlog por requisito

### RF-01 — Diagnóstico tecnológico

Relacionado con:

- PBI-001;
- PBI-002;
- PBI-003;
- PBI-004;
- PBI-005;
- PBI-006.

### RF-02 — Recolección de evidencia técnica

Relacionado con:

- PBI-008;
- PBI-009;
- PBI-010;
- PBI-011;
- PBI-012;
- PBI-013.

### RF-03 — Gestión documental

Relacionado con:

- PBI-017;
- PBI-018;
- PBI-023.

### RF-04 — Consulta mediante IA y RAG

Relacionado con:

- PBI-023;
- PBI-024;
- PBI-025;
- PBI-026;
- PBI-027.

### RF-05 — Evaluación de alternativas

Relacionado con:

- PBI-028;
- PBI-029;
- PBI-030;
- PBI-031.

### RF-06 — Recomendación de modernización

Relacionado con:

- PBI-032;
- PBI-033;
- PBI-034.

---

## 7. Requisitos no funcionales transversales

Los siguientes RNF no deben considerarse trabajo aislado únicamente al final.

### RNF-01 — Desempeño

Se validará progresivamente mediante:

- pruebas;
- métricas;
- healthchecks;
- baseline operativa.

### RNF-02 — Trazabilidad

Debe mantenerse relación entre:

- Raw Evidence;
- Normalized Data;
- Technical Assessment;
- Document Evidence;
- respuestas IA;
- evaluaciones;
- recomendaciones.

### RNF-03 — Seguridad

Debe mantenerse durante todos los Sprints:

- secretos fuera del repositorio;
- minimización de datos;
- revisión de evidencia;
- configuración externa;
- guardrails cuando exista tool calling.

### RNF-04 — Usabilidad

Las instrucciones y flujos deben ser comprensibles para usuarios no
especialistas en IA.

### RNF-05 — Compatibilidad y eficiencia

Las decisiones deberán considerar recursos existentes y permitir comparar:

- Local;
- Cloud;
- Híbrida.

---

## 8. Candidatos iniciales para Sprint 1

Los siguientes PBIs son candidatos de refinamiento para Sprint 1:

- PBI-001 — estructura mínima del backend;
- PBI-002 — Company;
- PBI-003 — TechnologyAssessment;
- PBI-004 — TechnologyResource;
- PBI-005 — TechnologyNeed;
- PBI-006 — API mínima de diagnóstico;
- PBI-007 — suite inicial de pruebas.

RF-02 podrá comenzar a refinarse durante Sprint 1 sin desplazar el Sprint
Goal principal de Backend Core.

La selección definitiva corresponde a F0.17 — Sprint 1 preparado.

---

## 9. Elementos deliberadamente diferidos

No se incorporan al trabajo activo inicial:

- SaaS multiempresa;
- autenticación empresarial;
- autorización compleja;
- microservicios;
- Kubernetes;
- message broker;
- event-driven architecture;
- múltiples agentes;
- MCP;
- fine-tuning;
- entrenamiento de modelos;
- monitoreo empresarial en tiempo real;
- acceso remoto obligatorio a infraestructura del cliente.

Estos elementos permanecen fuera de v1.0 o deberán ser reevaluados mediante
Product Backlog Refinement.

---

## 10. Regla de refinamiento

Antes de entrar a un Sprint, un PBI deberá:

- tener valor y alcance entendibles;
- poseer criterios de aceptación;
- tener dependencias conocidas;
- no contener una duda arquitectónica que impida comenzar;
- caber razonablemente dentro del Sprint;
- identificar la evidencia esperada.

Los criterios formales serán consolidados en F0.11 — Definition of Ready.

---

## 11. Resultado F0.9

La baseline inicial del Product Backlog establece trabajo ordenado para:

- Backend Core;
- Technical Assessment;
- Data + Containers;
- gestión documental;
- DevOps + Cloud;
- AI + RAG;
- evaluación de alternativas;
- recomendación de modernización;
- tool calling y agente acotado;
- hardening;
- demo y portafolio.

El backlog mantiene trazabilidad con los requisitos RF-01 a RF-06 y con los
RNF transversales.

---

## 12. Estado

**F0.9 — Product Backlog inicial: DONE**

Entregable:

`docs/project-management/product-backlog.md`

Siguiente bloque:

**F0.10 — Scrum Board**