# Registro de Decisiones de Arquitectura y Diseño (ADR)

Este documento registra el estado de todas las decisiones técnicas del proyecto **Sistema Profesor**, clasificadas rigurosamente según la taxonomía definida en la **Tarea 1.2**.

## Categorías de Clasificación

- **Decisión Confirmada:** Expresamente definida en la especificación original ([spec.md](file:///c:/Users/Nicolas/Desktop/tarea/spec.md)) o validada por el responsable del proyecto para el MVP.
- **Principio Arquitectónico Recomendado:** Directriz de diseño que rige el desarrollo y la calidad del sistema (seguridad, accesibilidad, separación de capas).
- **Decisión Propuesta Pendiente de Aprobación:** Recomendación técnica concreta del equipo que aguarda visto bueno del responsable.
- **Capacidad Opcional Futura:** Funcionalidad o patrón avanzado no obligatorio para el MVP inicial, supeditado a requisitos explícitos.
- **Decisión que Depende de Acuerdos Institucionales:** Definición condicionada a contratos, protocolos o decisiones de los módulos externos del Sistema de Gestión Académica.

---

## 1. Decisiones Confirmadas (Alcance del MVP)

| ID | Título | Descripción y Justificación | Clasificación |
| :--- | :--- | :--- | :--- |
| **DEC-001** | **Alcance del MVP** | El MVP comprende únicamente: (1) Autenticación del profesor, (2) Consulta de comisiones/materias asignadas en el período activo, (3) Consulta de alumnos por comisión, (4) Toma de asistencia con estados `presente`, `ausente` y `tarde`, (5) Consulta de historial de asistencia, (6) Registro de observaciones académicas por alumno, comisión y fecha. | **Confirmada** |
| **DEC-002** | **Exclusiones explícitas del MVP** | Quedan formalmente excluidas del MVP: calificaciones numéricas, comunicados generales y subida de archivos adjuntos. | **Confirmada** |
| **DEC-003** | **Arquitectura Desacoplada (Client-Server)** | La solución se estructurará como una aplicación cliente-servidor separada mediante una API REST. No se adoptará arquitectura monolítica clásica acoplada ni microservicios distribuidos sin justificación. | **Confirmada** |
| **DEC-004** | **Estados de Asistencia Cerrados** | Los únicos estados de asistencia admitidos en el sistema son exactamente tres: `presente`, `ausente` y `tarde`. No se admiten estados libres o variantes no tipadas. | **Confirmada** |
| **DEC-005** | **Autorización y Scope Docente Estricto** | Un profesor solo puede consultar información, tomar asistencia y asentar observaciones en las comisiones que tiene formalmente asignadas. | **Confirmada** |
| **DEC-006** | **Inmutabilidad del Historial para el Docente** | El historial de asistencia es de solo lectura para el profesor desde la interfaz del Sistema Profesor. | **Confirmada** |
| **DEC-007** | **Resolución Dinámica del Período Académico** | El período académico activo no debe estar fijado como una constante (hardcoded) en el código, sino resolverse mediante una regla de negocio explícita. | **Confirmada** |
| **DEC-008** | **Validación del Lado del Servidor (Zero Trust Client)** | Todas las reglas de negocio, integridad de datos y permisos se validan mandatoriamente en el backend. Ninguna validación de frontend se considera garantía de seguridad. | **Confirmada** |

---

## 2. Principios Arquitectónicos Recomendados

| ID | Principio | Justificación y Alcance | Clasificación |
| :--- | :--- | :--- | :--- |
| **DEC-PAR-01** | **Separación en 4 Niveles de Control de Acceso** | Desacoplar conceptualmente: (1) Identidad autenticada, (2) Rol del usuario, (3) Asignación académica de la comisión y (4) Autorización de operación sobre el recurso. Impide que un usuario con rol docente acceda a datos de comisiones no asignadas. | **Principio arquitectónico recomendado** |
| **DEC-PAR-02** | **Accesibilidad Universal Primero (WCAG 2.1 AA)** | Toda interfaz debe ser completamente operable vía teclado, legible con contraste superior a 4.5:1, con semántica ARIA para lectores de pantalla y orientada a móviles (*mobile-first*). | **Principio arquitectónico recomendado** |
| **DEC-PAR-03** | **Aislamiento del Dominio mediante Puertos** | Las reglas de negocio no deben depender de frameworks HTTP externos ni de detalles de persistencia remota, facilitando pruebas unitarias puras y reemplazo de adaptadores. | **Principio arquitectónico recomendado** |

---

## 3. Decisiones Técnicas Adoptadas e Inicializadas (Bloque 1)

| ID | Título | Definición Técnica y Justificación | Estado / Clasificación |
| :--- | :--- | :--- | :--- |
| **DEC-009** | **Stack de Frontend** | Implementado con **React 19 con TypeScript** mediante **Vite**. Enfoque modular, mobile-first y accesibilidad estricta (WCAG 2.1 AA) sin frameworks invasivos. | **Adoptada e inicializada (Bloque 1)** |
| **DEC-010** | **Stack de Backend** | Implementado con **Python 3.14 con Django 5.2 y Django REST Framework (DRF)**. Servidor desacoplado con `python-decouple` para gestión segura de variables de entorno. | **Adoptada e inicializada (Bloque 1)** |
| **DEC-011** | **Motor de Base de Datos** | Conexión configurada para **PostgreSQL 18** local mediante `psycopg 3.2`. Se provee fallback configurable a SQLite en `.env` (`DB_ENGINE`) para entornos de prueba aislados. | **Adoptada e inicializada (Bloque 1)** |
| **DEC-012** | **Especificación de Contratos de API** | Estándar **OpenAPI 3.0** implementado en backend con `drf-spectacular`. Endpoints `/api/schema/` y `/api/docs/` (Swagger UI) operativos. | **Adoptada e inicializada (Bloque 1)** |
| **DEC-013** | **Framework y Calidad de Código** | Pruebas unitarias e integración en backend con **pytest** y **pytest-django**; linter con **ruff**. En frontend, verificación de tipos estricta con **TypeScript (`tsc`)** y análisis estático con **oxlint**. | **Adoptada e inicializada (Bloque 1)** |
| **DEC-014** | **Contenerización del Entorno** | Utilizar **Docker y Docker Compose** para despliegue y evaluación homogénea. Docker no detectado en PATH local; no bloqueante para desarrollo local. | **Pendiente de evaluación de infraestructura** |
| **DEC-022** | **Arquitectura Hexagonal (Puertos y Adaptadores)** | Estructura de paquetes en `backend/apps/core/` con separación entre `domain/` (puertos), `application/` (casos de uso), `infrastructure/` (adaptadores) y `api/` (REST). | **Adoptada e inicializada (Bloque 1)** |
| **DEC-023** | **Puertos de Integración Desacoplados** | Interfaces abstractas formalizadas en `backend/apps/core/domain/ports.py` (`IAuthenticationGateway`, `IAcademicDataGateway`, `IAttendanceGateway`, `IObservationRepository`). | **Adoptada e inicializada (Bloque 1)** |
| **DEC-025** | **Reglas Conceptuales de Instancias de Clase e Idempotencia** | Distinción formal entre fecha de calendario e instancia de clase consolidada en SPEC-002 v1.1 para soportar múltiples clases/turnos en el mismo día y reintentos idempotentes. | **Consolidada en modelo de dominio** |
| **DEC-026** | **Identificadores de Entidad en Formato UUIDv4** | Utilizar identificadores UUIDv4 para entidades compartidas (`profesor_id`, `alumno_id`, `comision_id`) para prevenir vulnerabilidades de enumeración. | **Confirmada en SPEC-002** |

---

## 4. Capacidades Opcionales Futuras (No Obligatorias para el MVP)

| ID | Capacidad | Descripción y Condición de Activación | Clasificación |
| :--- | :--- | :--- | :--- |
| **DEC-OPT-01** | **Patrón Outbox y Sincronización en Segundo Plano** | Mecanismo de despacho asíncrono para reintentar el envío de asistencias a sistemas externos con retroceso exponencial. **No es parte del MVP inicial**; solo se implementará si los requisitos de conectividad del aula o contratos externos lo hacen mandatorio. | **Capacidad opcional futura** |
| **DEC-OPT-02** | **Soporte Offline Completo en Frontend** | Almacenamiento local en cliente (IndexedDB) para operar sin red prolongada. **No es parte del MVP inicial**; se asume conexión estándar en la institución durante el dictado de clases. | **Capacidad opcional futura** |

---

## 5. Decisiones que Dependen de Acuerdos Institucionales

| ID | Cuestión Abierta | Escenarios o Alternativas | Acción Requerida | Clasificación |
| :--- | :--- | :--- | :--- | :--- |
| **DEC-017** | **Persistencia Oficial y Propiedad de Asistencias** | **Escenario A:** Módulo Central de Asistencia es la fuente oficial y persiste el registro. El Sistema Profesor consume su API vía adaptador.<br>**Escenario B:** El Sistema Profesor registra localmente y sincroniza con el módulo central. | Acordar formalmente con el equipo del módulo de Asistencia cuál de los dos escenarios regirá el sistema institucional. | **Decisión que depende de acuerdos institucionales** |
| **DEC-016 / DEC-028** | **Protocolo y Formato de Token de Autenticación** | Se contemplan opciones (JWT asimétrico, OAuth2/OIDC, o sesión compartida), pero **no se asume ninguna como definitiva** hasta recibir la especificación oficial del IdP central. | Recibir del equipo de Autenticación el protocolo y mecanismo de verificación de credenciales. | **Decisión que depende de acuerdos institucionales** |
| **DEC-018** | **Propiedad y Sincronización de Datos Maestros (Alumnos/Comisiones)** | El SGA Central es la fuente oficial. Resta definir si el Sistema Profesor consulta en tiempo real o mantiene una réplica de lectura local (y con qué frecuencia o evento se actualiza). | Definir con el equipo del SGA el mecanismo de consulta o réplica de nóminas y comisiones. | **Decisión que depende de acuerdos institucionales** |
| **DEC-019** | **Identificadores Compartidos entre Sistemas** | Validar si los sistemas externos expondrán UUIDs o identificadores numéricos/legajos institucionales. | Coordinar con los equipos del SGA y Asistencia el formato de claves foráneas compartidas. | **Decisión que depende de acuerdos institucionales** |
| **DEC-021** | **Política de Rectificación de Asistencia en el Día** | Definir si se autoriza al docente a corregir una asistencia dentro de la misma jornada de clase antes del cierre definitivo de la planilla. | Consulta al área académica sobre la flexibilidad de edición inmediata vs. inmutabilidad estricta. | **Decisión que depende de acuerdos institucionales** |
