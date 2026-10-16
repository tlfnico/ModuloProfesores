# Comparativa de Alternativas Arquitectónicas — Sistema Profesor

**Documento:** Evaluación técnica de alternativas de arquitectura e integración  
**Proyecto:** Sistema de Gestión Académica — Sistema Profesor  
**Etapa:** Etapa 1 / Tarea 1.1  
**Estado:** Propuesta técnica para discusión con el equipo  

---

## 1. Contexto y Desafío Arquitectónico

El **Sistema Profesor** debe implementar las funcionalidades críticas del MVP (acceso docente, consulta de comisiones/alumnos, toma de asistencia con estados cerrado `presente/ausente/tarde`, historial de asistencia y observaciones académicas). 

El sistema no opera de forma aislada: pertenece a un ecosistema más amplio (Sistema de Gestión Académica) que contempla módulos de **Autenticación Institucional** y **Asistencia Central**, cuyos contratos técnicos definitivos e implementaciones aún no están disponibles.

El objetivo de este documento es evaluar rigurosamente tres alternativas arquitectónicas bajo criterios de ingeniería de software, mantenibilidad, seguridad y viabilidad operativa.

---

## 2. Alternativas Analizadas

### Opción A: Monolito Modular
Una única aplicación y base de datos compartida para todos los módulos del Sistema de Gestión Académica (Autenticación, Alumnos, Profesores, Asistencias), donde el Sistema Profesor es un paquete o módulo interno (ej. Django App `profesores`) con límites lógicos estrictos.

- **Frontend:** SPA integrada o vistas renderizadas con React embebido.
- **Backend:** Una única base de código y un único proceso en ejecución.
- **Datos:** Una base de datos relacional común con esquemas o tablas separadas lógicamente.

### Opción B: Aplicaciones y Servicios Independientes (APIs HTTP Distribuidas)
El Sistema Profesor es un servicio totalmente aislado (frontend y backend propios) que se comunica exclusivamente mediante llamadas HTTP REST síncronas con los servicios remotos de Autenticación, Gestión Académica Central y Asistencia Institucional.

- **Frontend:** SPA independiente (React + TypeScript).
- **Backend:** API REST autónoma que no persiste datos académicos ni de asistencia localmente; actúa como un proxy orquestador (*Backend for Frontend - BFF*).
- **Datos:** No almacena Alumnos, Comisiones ni Asistencias; todo se consulta y escribe en tiempo real contra APIs externas.

### Opción C: Arquitectura Híbrida / Desacoplada con Puertos y Adaptadores (Recomendada)
El Sistema Profesor es una aplicación web autónoma (Frontend SPA desacoplado + Backend modular en Django/DRF) estructurada internamente bajo el patrón de **Puertos y Adaptadores (Arquitectura Hexagonal)**.
Mantiene un almacenamiento local en PostgreSQL para sus datos nativos (Observaciones, asignaciones en caché, registros transaccionales de asistencia tomados en aula) y se conecta con los sistemas institucionales externos mediante **adaptadores de integración reemplazables**.

- **Frontend:** SPA independiente en React + TypeScript optimizada para accesibilidad y dispositivos móviles en el aula.
- **Backend:** Módulos de dominio bien definidos (`acceso`, `comisiones`, `asistencia`, `observaciones`) desacoplados de los detalles de infraestructura externa.
- **Integración:** El dominio interactúa con interfaces abstractas (`IAuthenticationGateway`, `IAttendanceGateway`, `IAcademicDataGateway`). Durante el desarrollo se utilizan adaptadores en memoria o locales; una vez provistos los contratos externos, se conectan los adaptadores HTTP definitivos sin modificar la lógica del dominio.
- **Datos:** Persistencia transaccional local en PostgreSQL para resiliencia ante caídas de red, con sincronización idempotente hacia el módulo central de asistencia.

---

## 3. Matriz Comparativa Exhaustiva

| Criterio de Evaluación | Opción A: Monolito Modular | Opción B: Servicios Independientes (HTTP) | Opción C: Híbrida con Puertos y Adaptadores (Recomendada) |
| :--- | :--- | :--- | :--- |
| **1. Complejidad inicial y curva de aprendizaje** | **Muy Baja:** Un único repositorio, un solo entorno local, sin necesidad de mocks de red ni infraestructura distribuida. | **Muy Alta:** Requiere coordinar múltiples servicios, contratos de red, manejo de latencia y fallos parciales desde el día uno. | **Baja - Moderada:** Un único servicio principal para el Sistema Profesor con abstracciones limpias en código. Excelente relación valor/esfuerzo. |
| **2. Facilidad de desarrollo con agentes de programación** | **Alta:** Todo el contexto de modelos y funciones reside en el mismo proyecto. Sin embargo, bases de código masivas pueden saturar el contexto. | **Baja:** El agente necesita simular o conocer endpoints externos inexistentes; riesgo de alucinación de contratos de red. | **Muy Alta:** Las interfaces (puertos) delimitan con precisión el alcance de cada tarea. El agente puede implementar adaptadores mock locales fácilmente. |
| **3. Mantenimiento y pruebas** | **Alta en unitarias, Media en despliegue:** Pruebas unitarias ultrarrápidas en memoria. Riesgo de acoplamiento accidental en base de datos. | **Baja:** Requiere pruebas complejas de integración de red, contratos (Pact) y entornos mockeados pesados. | **Muy Alta:** Pruebas unitarias de dominio puras y rápidas con mocks in-memory; pruebas de integración aisladas por adaptador. |
| **4. Seguridad y autorización** | **Alta:** Control de permisos directo en memoria y consultas SQL con restricciones estrictas de rol y profesor. | **Media - Compleja:** Requiere propagación segura de tokens (JWT/OAuth2), validación en cada salto y gestión de secretos inter-servicio. | **Muy Alta:** Autenticación delegable por adaptador; autorización y control de scope docente (*Object-Level Permissions*) validado localmente con Zero Trust. |
| **5. Independencia entre equipos** | **Baja:** Requiere que todos los equipos acuerden el mismo lenguaje, framework, migraciones de base de datos y calendario de despliegue. | **Muy Alta:** Cada equipo despliega y versiona su servicio libremente. | **Alta:** El equipo del Sistema Profesor avanza de forma autónoma sin depender de que los otros equipos tengan listos sus servicios. |
| **6. Integración con Autenticación y Asistencia (sin contratos)** | **Bloqueante:** Si los otros módulos no están listos en el monolito, no se puede estructurar el código conjunto. | **Bloqueante o Frágil:** Sin endpoints HTTP reales, el desarrollo se detiene o se basa en endpoints ficticios inventados. | **Óptima:** Se definen interfaces internas (*Ports*). El desarrollo del MVP avanza con adaptadores simulados sin bloquearse. |
| **7. Consistencia y propiedad de los datos** | **Máxima (ACID):** Transacciones locales atómicas. Riesgo de que múltiples equipos toquen las mismas tablas sin disciplina. | **Eventual / Baja:** Requiere transacciones distribuidas o patrones Saga ante fallos al guardar asistencias en servicios remotos. | **Alta y Resiliente:** ACID local para registros en aula con garantías de unicidad e idempotencia, desacoplado de la sincronización externa. |
| **8. Despliegue, observabilidad y costos operativos** | **Muy Económico:** Un único contenedor Docker o servidor. Observabilidad trivial (logs centralizados de un proceso). | **Costoso y Complejo:** Múltiples contenedores, API Gateways, balanceadores, distributed tracing (Jaeger/Zipkin). | **Económico y Controlado:** Un solo contenedor para el Sistema Profesor; no impone sobrecostos operativos en fase de MVP. |
| **9. Evolutividad y escalabilidad futura** | **Media:** Escala como un todo. Si un módulo demanda alta concurrencia, se replica la aplicación completa. | **Alta:** Cada servicio escala independientemente. | **Muy Alta:** Gracias a la separación de puertos y adaptadores, cualquier módulo interno puede extraerse a un microservicio en el futuro sin reescribir el dominio. |

---

## 4. Conclusión del Análisis

1. **Descarte de la Opción A (Monolito Global Completo):** Aunque técnicamente simple, es organizacionalmente inviable si los otros módulos del SGA están a cargo de equipos independientes con tecnologías o cronogramas distintos. Exigiría unificar repositorios y deploys institucionales antes de avanzar con el Sistema Profesor.
2. **Descarte de la Opción B (Microservicios puros con llamadas HTTP síncronas en tiempo real):** Muy riesgoso para un MVP. Si el servicio de Asistencia o de Red falla mientras el docente está pasando lista en un aula con mala conectividad, el sistema quedaría inoperable, violando la regla de usabilidad y baja carga cognitiva. Además, al no existir contratos aún, implementar clientes HTTP hoy implicaría inventar endpoints que luego tendrán que desecharse.
3. **Selección de la Opción C (Arquitectura Híbrida / Puertos y Adaptadores):** Provee la mejor combinación de autonomía, velocidad de desarrollo, resiliencia operativa y protección frente a la falta de contratos de los sistemas externos.
