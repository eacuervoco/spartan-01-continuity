# ContinuitY Platform
## F0.8 — Architecture v0

**Proyecto:** Spartan #01  
**Producto:** ContinuitY Platform  
**Fase:** F0 — Project Foundation  
**Bloque:** F0.8 — Architecture v0  
**Versión:** 0.1  
**Estado:** Baseline inicial  
**Fecha:** Septiembre 2026

---

# 1. Propósito

Este documento define la arquitectura inicial de ContinuitY Platform.

Architecture v0 traduce los requisitos, la trazabilidad y el modelo de
dominio definidos durante F0.5, F0.6 y F0.7 en una organización técnica
inicial.

La arquitectura deberá evolucionar conforme aparezcan responsabilidades
reales.

No deberán introducirse capas, servicios, bases de datos, componentes de IA
o infraestructura únicamente por anticipación.

---

# 2. Principios arquitectónicos

ContinuitY adopta los siguientes principios:

- separación de responsabilidades;
- arquitectura evolutiva;
- Clean Architecture pragmática;
- dominio independiente de infraestructura cuando resulte útil;
- evidencia antes que interpretación;
- automatización determinista antes que agente;
- IA únicamente cuando exista un requisito y una métrica;
- seguridad y minimización de datos;
- trazabilidad;
- Local + Cloud mediante Dual-Lab Engineering;
- documentación y decisiones versionadas en Git.

---

# 3. Drivers arquitectónicos

La arquitectura debe soportar inicialmente los siguientes drivers:

| Driver | Consecuencia arquitectónica |
|---|---|
| Diagnóstico tecnológico | Debe existir un dominio independiente para assessments, recursos y necesidades |
| Captura HW/SO | La evidencia original debe mantenerse separada de los datos interpretados |
| `ContinuitY_assessment.txt` | Se requiere un mecanismo de importación, validación y parsing |
| Windows + Linux | El contrato de entrada debe ser común aunque cambie el método de recolección |
| Gestión documental | Los documentos requieren metadatos y una referencia persistente |
| RAG futuro | La documentación deberá poder utilizarse posteriormente como fuente de evidencia |
| Evaluación Local/Cloud/Híbrida | Los resultados deberán poder compararse sin acoplar el dominio a AWS |
| Recomendación | Debe diferenciarse evidencia, evaluación y decisión |
| Recursos limitados | La solución local debe poder ejecutarse en SpartanLab |
| Cloud | Las capacidades podrán compararse con alternativas AWS sin exigir equivalencia 1:1 |

---

# 4. Vista lógica de alto nivel

ContinuitY v0 se organiza conceptualmente en:

                   ┌─────────────────────┐
                   │      Usuario        │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │    API / Interface  │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ Application Layer   │
                   │ Use Cases           │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │    Domain Layer     │
                   │ Business Concepts   │
                   └──────────┬──────────┘
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
      Persistence       File Evidence     External Services
                                             Future

La dependencia principal debe orientarse hacia el dominio.

Los detalles de infraestructura no deberán gobernar las reglas del negocio.

---

# 5. Capas iniciales

## 5.1 Domain

Responsabilidad:

Representar conceptos y reglas propias de ContinuitY.

Conceptos identificados inicialmente:

- Company
- TechnologyAssessment
- TechnologyResource
- TechnologyNeed
- TechnicalEvidence
- HardwareSnapshot
- TechnicalDocument
- TechnologyEvaluation
- ModernizationRecommendation

El dominio no deberá depender directamente de FastAPI, PostgreSQL, AWS,
Ollama u otros mecanismos de infraestructura.

---

## 5.2 Application

Responsabilidad:

Coordinar los casos de uso del producto.

Ejemplos futuros:

CreateCompany
CreateAssessment
RegisterTechnologyResource
ImportTechnicalEvidence
ParseTechnicalAssessment
RegisterTechnicalDocument
RegisterTechnologyEvaluation
CreateModernizationRecommendation

Los nombres anteriores son conceptuales y podrán evolucionar durante la
implementación.

---

## 5.3 Interface / API

Responsabilidad:

Permitir que usuarios o sistemas externos invoquen capacidades de
ContinuitY.

La implementación inicial prevista utilizará una API HTTP.

FastAPI es la tecnología candidata inicial debido al stack definido para
Spartan #01.

La API no deberá contener reglas de negocio que pertenezcan al dominio.

---

## 5.4 Infrastructure

Responsabilidad:

Implementar detalles técnicos necesarios para persistencia, filesystem,
parsing, servicios externos y ejecución.

Ejemplos futuros:

- persistencia PostgreSQL;
- almacenamiento de evidencia;
- parser de `ContinuitY_assessment.txt`;
- configuración;
- logging;
- integración AWS;
- servicios de IA;
- retrieval;
- tool calling.

La infraestructura podrá cambiar sin redefinir las reglas principales del
dominio.

---

# 6. Arquitectura de RF-02 — Technical Assessment

RF-02 introduce un pipeline específico:

Cliente
   |
   v
Instrucciones Windows / Linux
   |
   v
ContinuitY_assessment.txt
   |
   v
Import
   |
   v
Validation
   |
   +------------> Raw Evidence
   |
   v
Parser
   |
   v
Normalized Data
   |
   v
HardwareSnapshot
   |
   v
TechnologyAssessment

La versión original del archivo deberá preservarse como evidencia.

El parser no deberá modificar la evidencia original.

---

# 7. Contrato conceptual del assessment

Todos los sistemas operativos soportados deberán producir un artefacto
compatible con el concepto:

`ContinuitY_assessment.txt`

Aunque los comandos cambien entre Linux y Windows, ContinuitY deberá
interpretar secciones funcionalmente equivalentes.

Categorías iniciales:

METADATA
HOSTNAME
SYSTEM
CPU
MEMORY
STORAGE
FILESYSTEM
NETWORK

Cada formato deberá incluir una versión de assessment que permita evolucionar
los parsers sin perder trazabilidad.

---

# 8. Raw Evidence vs Normalized Data

La arquitectura distingue tres niveles:

## Raw Evidence

Información obtenida directamente desde el recurso evaluado.

Ejemplo:

`ContinuitY_assessment.txt`

No deberá alterarse después de su incorporación.

## Normalized Data

Representación estructurada producida a partir de Raw Evidence.

Ejemplo:

hostname
operating_system
cpu_model
cpu_cores
memory_total
storage_total

## Assessment

Interpretación contextual de la evidencia y datos normalizados.

Ejemplo:

"El equipo se encuentra operativo pero presenta recursos limitados para el
workload evaluado."

Esta separación permite auditar posteriormente cómo se obtuvo una
conclusión.

---

# 9. Persistencia

La estrategia inicial prevista para datos estructurados será PostgreSQL.

Los siguientes tipos de información son candidatos a persistencia
relacional:

- empresas;
- assessments;
- recursos;
- necesidades;
- metadatos de evidencia;
- documentos;
- evaluaciones;
- recomendaciones.

La evidencia técnica original y los documentos no deberán almacenarse
obligatoriamente dentro de la base de datos.

La arquitectura deberá permitir que el contenido binario o textual pueda
residir en almacenamiento de archivos u objetos, conservando en base de
datos su referencia y metadata.

La decisión física definitiva deberá validarse durante los Sprints
correspondientes.

---

# 10. Documentación técnica

TechnicalDocument representa metadata y referencia documental.

Conceptualmente:

TechnicalDocument
      |
      +-- metadata
      |
      +-- reference
      |
      +-- content/storage

El almacenamiento físico podrá comenzar localmente y evolucionar hacia
object storage cuando exista una necesidad real.

La arquitectura no presupone todavía S3.

---

# 11. IA y RAG

RF-04 requiere una futura capacidad de consulta documental utilizando IA y
RAG.

Architecture v0 reserva el límite funcional:

User Query
    |
    v
Retrieval
    |
    v
Document Evidence
    |
    v
Generation
    |
    v
Referenced Response

No se define todavía:

- proveedor LLM;
- modelo;
- embeddings;
- vector database;
- framework RAG;
- proveedor cloud.

Estas decisiones corresponden al Sprint de AI + RAG y deberán basarse en
evaluación y baseline.

---

# 12. Agentes

Architecture v0 no introduce un agente como componente obligatorio.

Antes de incorporar comportamiento agentic deberá demostrarse que:

1. existe una tarea que requiere selección dinámica de acciones;
2. una solución determinista resulta insuficiente;
3. existen herramientas claramente delimitadas;
4. existen controles y evaluación.

Tool calling y agentes serán capacidades evolutivas, no fundamentos de
Architecture v0.

---

# 13. Dual-Lab Engineering

ContinuitY tendrá dos contextos de experimentación:

SpartanLab Local

y

AWS / Cloud Lab

No deberán considerarse implementaciones obligatoriamente idénticas.

El objetivo es comparar alternativas utilizando criterios como:

- costo;
- rendimiento;
- complejidad;
- privacidad;
- seguridad;
- mantenibilidad;
- latencia;
- operación.

Cuando una comparación produzca una decisión arquitectónica relevante,
deberá documentarse mediante ADR.

---

# 14. Deployment conceptual local

La evolución esperada del entorno local es:

             User
               |
               v
          HTTP / API
               |
               v
        ContinuitY Backend
          Python/FastAPI
               |
        ┌──────┴──────┐
        ▼             ▼
   PostgreSQL      File Storage
                       |
                       v
              Raw Evidence / Docs

Posteriormente podrán incorporarse:

- contenedores;
- reverse proxy;
- observabilidad;
- AI Service;
- retrieval;
- tool calling.

No todos estos componentes pertenecen al incremento inicial.

---

# 15. Deployment conceptual cloud

AWS será utilizado como entorno de aprendizaje, comparación y eventual
ejecución de capacidades seleccionadas.

Conceptualmente:

              ContinuitY
                  |
        ┌─────────┴─────────┐
        ▼                   ▼
   SpartanLab              AWS
      Local              Alternative
        |                   |
        └─────────┬─────────┘
                  ▼
         Engineering Decision

No se define en Architecture v0 un deployment productivo obligatorio sobre
AWS.

Cada servicio AWS deberá incorporarse únicamente cuando un requisito,
riesgo o experimento justifique su uso.

---

# 16. Seguridad

Architecture v0 establece las siguientes restricciones:

No deberán almacenarse en el repositorio:

- passwords;
- API keys;
- tokens;
- credenciales;
- secretos;
- datos personales innecesarios;
- información propietaria real.

El Technical Assessment deberá aplicar minimización de datos.

El cliente deberá poder revisar `ContinuitY_assessment.txt` antes de
entregarlo.

La futura configuración sensible deberá mantenerse fuera del código fuente.

---

# 17. Observabilidad

La arquitectura deberá permitir incorporar progresivamente:

logging
healthchecks
metrics

No se requiere implementar toda la observabilidad durante Fase 0.

Los componentes deberán proporcionar evidencia suficiente para diagnosticar
fallos conforme aumente la madurez de la plataforma.

---

# 18. Testing

La arquitectura deberá permitir pruebas en diferentes niveles:

Domain Tests
Application Tests
Integration Tests
API Tests

F0.15 establecerá la primera suite mínima mediante pytest.

Las pruebas deberán crecer junto con los incrementos y no como una fase
separada al final.

---

# 19. Estructura de código candidata

La estructura inicial deberá aparecer únicamente cuando exista código que
justifique cada responsabilidad.

Conceptualmente:

src/
└── continuity/
    ├── domain/
    ├── application/
    ├── infrastructure/
    └── api/

Esta estructura no obliga a crear directorios vacíos durante F0.8.

La primera implementación deberá utilizar la estructura mínima necesaria.

---

# 20. Decisiones explícitamente diferidas

Architecture v0 no decide todavía:

Database schema definitivo
ORM
vector database
embedding model
LLM
RAG framework
AWS deployment target
authentication architecture
frontend framework
message broker
microservices
event-driven architecture
Kubernetes
agent framework
MCP architecture

Estas decisiones deberán aparecer cuando exista una necesidad real.

---

# 21. ADR candidatos

Las siguientes decisiones podrán requerir ADR cuando llegue el momento:

PostgreSQL como persistencia principal
Raw Evidence fuera de PostgreSQL
Storage local vs object storage
FastAPI como interfaz HTTP
Local AI vs Cloud AI
Vector storage
Deployment AWS
Agentic architecture

No es necesario crear los ADR hasta que exista una decisión real y sus
alternativas puedan evaluarse.

---

# 22. Arquitectura inicial resumida

                    ┌──────────────────────┐
                    │       Cliente        │
                    └──────────┬───────────┘
                               │
                     Assessment / Requests
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Interface/API     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     Application      │
                    │      Use Cases       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       Domain         │
                    │ Business Rules       │
                    └──────────┬───────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
          PostgreSQL      File Evidence    Integrations
                             / Docs          Future
                                                |
                                      AI / AWS / Tools
                                        when required

---

# 23. Resultado F0.8

Architecture v0 establece:

- límites principales del sistema;
- separación Domain / Application / Interface / Infrastructure;
- pipeline de Technical Assessment;
- separación Raw Evidence / Normalized Data / Assessment;
- estrategia inicial de persistencia;
- estrategia documental;
- límites futuros para IA/RAG/agentes;
- principio Dual-Lab;
- restricciones de seguridad;
- estrategia evolutiva.

---

# 24. Estado

**F0.8 — Architecture v0: DONE**

Entregable:

`docs/architecture/architecture-v0.md`

Baseline:

`Architecture v0.1`

Siguiente bloque:

**F0.9 — Product Backlog inicial**