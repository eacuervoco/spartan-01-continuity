# ContinuitY Platform

Modernización y continuidad tecnológica para PYMEs, basada en evidencia,
aprovechamiento de infraestructura existente y adopción selectiva de IA.

## Visión

ContinuitY Platform ayuda a una organización a decidir qué modernizar,
qué recursos tecnológicos puede seguir aprovechando y dónde la
inteligencia artificial produce una mejora medible para el negocio.

La plataforma trata la modernización como un problema de decisión de
ingeniería, no como una compra de tecnología.

## Problema

Muchas pequeñas y medianas empresas poseen:

- infraestructura tecnológica heterogénea;
- equipos aún aprovechables pero no evaluados;
- documentación técnica distribuida;
- conocimiento difícil de consultar;
- incertidumbre sobre cuándo usar soluciones locales, cloud o híbridas.

ContinuitY busca convertir ese contexto en información estructurada,
evidencia técnica y decisiones justificables.

## Flujo objetivo

Empresa  
→ diagnóstico  
→ captura de evidencia técnica  
→ evaluación de recursos  
→ organización documental  
→ pruebas  
→ medición  
→ comparación  
→ recomendación de modernización

## Capacidades previstas para v1.0

- diagnóstico tecnológico;
- recolección de evidencia técnica de hardware y sistema operativo;
- gestión de documentación técnica;
- consulta mediante IA y RAG;
- evaluación de alternativas local, cloud e híbrida;
- recomendación de modernización basada en evidencia.

## Enfoque de ingeniería

Spartan #01 se desarrolla utilizando progresivamente:

- Python;
- FastAPI;
- PostgreSQL;
- Docker y Docker Compose;
- pytest;
- CI;
- logging y healthchecks;
- IA local;
- RAG;
- tool calling;
- un agente acotado;
- AWS como entorno de aprendizaje y comparación.

Estas tecnologías se incorporan únicamente cuando soportan un requisito,
reducen un riesgo o permiten demostrar una mejora medible.

## Technical Assessment

ContinuitY incorpora un mecanismo inicial de recolección de evidencia técnica
sin requerir acceso remoto al equipo del cliente.

El cliente recibe instrucciones compatibles con el sistema operativo
soportado, ejecuta localmente los comandos suministrados y genera:

`ContinuitY_assessment.txt`

El archivo puede ser revisado por el cliente antes de ser entregado y se
utiliza como evidencia técnica para el proceso de diagnóstico.

La v1.0 contempla inicialmente:

- Linux;
- Windows.

ContinuitY diferencia entre:

- evidencia original;
- datos normalizados;
- interpretación;
- evaluación;
- recomendación.

Una evidencia técnica no constituye por sí sola una recomendación de
modernización.

## Dual-Lab Engineering

ContinuitY se desarrolla mediante dos entornos complementarios.

### SpartanLab

Entorno local persistente utilizado para construir, probar y operar
componentes del sistema.

### AWS

Entorno cloud utilizado para laboratorios, validaciones y comparaciones
de arquitectura.

El objetivo no es construir copias idénticas, sino comparar trade-offs
como:

- costo;
- seguridad;
- privacidad;
- latencia;
- complejidad;
- mantenibilidad;
- operación.

## Caso de estudio

La primera validación utiliza el caso ficticio:

**TecniRed Sabana S.A.S.**

Empresa dedicada a servicios técnicos de redes de datos, CCTV y control
de acceso.

Este caso permite validar diagnóstico, recolección de evidencia técnica,
gestión documental, evaluación de infraestructura y decisiones de
modernización.

## Estado del proyecto

**Spartan #01 — ContinuitY Platform**

- Estado actual: Fase 0 — Project Foundation
- Marco de gestión: Scrum
- Horizonte v1.0: 12 semanas
- Versión actual: Foundation
- Fuente de verdad: GitHub
- Arquitectura: evolutiva y pragmática

## Roadmap general

| Periodo | Foco |
|---|---|
| Semana 1 | Project Foundation |
| Semanas 2–3 | Backend Core |
| Semanas 4–5 | Data + Containers |
| Semanas 6–7 | DevOps + Cloud |
| Semanas 8–9 | AI + RAG |
| Semanas 10–11 | Agentic Spartan |
| Semana 12 | Hardening + Portfolio |

## Principios

- aprovechar antes de reemplazar;
- medir antes de recomendar;
- preservar evidencia antes de interpretarla;
- automatizar antes de introducir un agente;
- utilizar IA únicamente cuando aporte valor demostrable;
- mantener trazabilidad entre problema, requisito, implementación y evidencia;
- favorecer soluciones simples, mantenibles y evolutivas;
- proteger secretos, credenciales y datos sensibles.

## Documentación principal

La documentación viva de ingeniería se mantiene dentro del repositorio.

Estructura principal:

```text
docs/
├── project-management/
│   ├── project-vision.md
│   ├── scope-v1.md
│   └── product-backlog.md
├── requirements/
│   ├── requirements-v1.0.md
│   └── traceability-matrix.md
├── uml/
│   ├── README.md
│   ├── use-cases-v0.puml
│   └── domain-model-v0.puml
└── architecture/
    └── architecture-v0.md
```

## Estado de desarrollo

El proyecto se encuentra actualmente en construcción.

La documentación de gestión y las decisiones de ingeniería se mantienen
versionadas dentro del repositorio.

## Autor

**Edwin A. Cuervo**  
SpartanLab