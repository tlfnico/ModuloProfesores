# Manual del Sistema — SGA Sistema Profesor

**Proyecto:** Sistema de Gestión Académica — Módulo Profesor  
**Última actualización:** 2026-10-16  
**Documentos relacionados:** [ARCHITECTURE.md](../ARCHITECTURE.md) | [DECISIONS.md](../DECISIONS.md) | [PROGRESS.md](../PROGRESS.md) | [GETTING_STARTED.md](./GETTING_STARTED.md)

---

## 1. ¿Qué problema resuelve?

En las instituciones educativas de nivel terciario, los profesores necesitan herramientas ágiles para gestionar la asistencia de sus alumnos, consultar la composición de sus comisiones y registrar observaciones pedagógicas de seguimiento.

El **Sistema Profesor** es un módulo del **Sistema de Gestión Académica (SGA)** que centraliza estas funciones en una aplicación web accesible desde el navegador, pensada para usarse desde el aula con dispositivos móviles o de escritorio.

---

## 2. Alcance funcional del MVP

El MVP (Producto Mínimo Viable) contempla seis funcionalidades:

| # | Funcionalidad | Estado |
| :--- | :--- | :--- |
| F1 | Consulta de comisiones y materias asignadas en el período activo | ✅ Implementada y verificada |
| F2 | Consulta de la nómina de alumnos de una comisión | ✅ Implementada y verificada |
| F3 | Toma de asistencia con estados `presente`, `ausente` y `tarde` | ✅ Implementada (validación en servidor; persistencia oficial pendiente de DEC-017) |
| F4 | Consulta del historial de asistencia | ✅ Implementada (validación en servidor; persistencia oficial pendiente de DEC-017) |
| F5 | Registro de observaciones académicas por alumno, comisión y fecha | ✅ Implementada y verificada |
| F6 | Acceso del profesor mediante autenticación | ⏳ Provisional (cabecera `X-Profesor-Id`; autenticación institucional pendiente) |

### Exclusiones explícitas del MVP

- Calificaciones numéricas, escalas de notas.
- Comunicados generales y mensajería.
- Carga de archivos adjuntos.
- Gestión de matrículas o planes de estudio.

---

## 3. Usuarios y roles

| Rol | Descripción | Permisos principales |
| :--- | :--- | :--- |
| **Profesor** | Docente con asignación académica formal en una o más comisiones. | Consultar sus comisiones, ver la nómina de alumnos, tomar asistencia en sus comisiones, registrar observaciones pedagógicas. |
| **Administrador / SGA Central** | Sistema externo que gestiona los datos maestros (alumnos, comisiones, materias, asignaciones). | Fuente oficial de los datos de referencia. El Sistema Profesor los consume en modo lectura. |

> **Nota:** El Módulo Preceptor (desarrollado por otro integrante del equipo) gestiona funcionalidades complementarias. Ver [MODULES_AND_INTEGRATION.md](./MODULES_AND_INTEGRATION.md) para los límites entre módulos.

---

## 4. Conceptos principales

Estos son los términos clave del dominio. El detalle completo se encuentra en [SPEC-002](../specs/SPEC-002-modelo-dominio.md).

| Concepto | Significado |
| :--- | :--- |
| **Período Lectivo** | Intervalo temporal académico (ej. *Primer Cuatrimestre 2026*) que enmarca las cursadas. |
| **Comisión** | Agrupamiento organizativo (división/turno/año) donde confluyen alumnos, docentes y materias. |
| **Materia** | Espacio curricular del plan de estudios (ej. *Programación I*). |
| **Asignación Docente** | Vínculo formal entre un profesor y una comisión para un período. |
| **Instancia de Clase** | Sesión pedagógica concreta. Una comisión puede tener varias instancias en el mismo día (ej. teórico a la mañana, práctico a la tarde). |
| **Registro de Asistencia** | Estado de presencia de un alumno en una instancia de clase: `PRESENTE`, `AUSENTE` o `TARDE`. |
| **Observación Académica** | Nota de texto libre asociada a un alumno, comisión y fecha. Registra la fecha del hecho pedagógico y la fecha de creación. |

---

## 5. Módulos del SGA

El Sistema de Gestión Académica está compuesto por módulos independientes desarrollados por distintos integrantes:

| Módulo | Responsable | Estado |
| :--- | :--- | :--- |
| **Módulo Profesor** | Nicolás | Dominio implementado, API REST funcional, interfaz con rediseño visual, pruebas automatizadas. |
| **Módulo Preceptor** | Otro integrante | En desarrollo paralelo. |
| **Autenticación institucional** | Por definir | Pendiente de acuerdo institucional. Se usa cabecera provisional `X-Profesor-Id`. |
| **SGA Central (datos maestros)** | Institución | Fuente oficial de alumnos, comisiones, materias y asignaciones. |

---

## 6. Reglas de negocio principales

Las reglas completas están documentadas en [SPEC-002 §5](../specs/SPEC-002-modelo-dominio.md). A continuación las más relevantes para el trabajo diario:

### Scope Docente (R-DOC-01)

Un profesor solo puede acceder a las comisiones donde tiene una asignación docente vigente en el período activo. Esta verificación se hace siempre en el backend, sin confiar en el frontend.

### Estados de Asistencia (R-ASI-01)

Solo tres estados válidos: `PRESENTE`, `AUSENTE`, `TARDE`. No existen estados libres ni justificaciones en el MVP.

### Toma Parcial (R-ASI-02)

Una toma de asistencia puede quedar incompleta. Un alumno sin estado registrado **no** se considera automáticamente ausente.

### Idempotencia (R-ASI-03)

Si se reenvía la misma asistencia por un corte de red, el sistema no duplica registros.

### Observaciones con doble fecha (R-OBS-04)

Cada observación registra la fecha del hecho pedagógico (elegida por el docente) y la fecha de creación en el sistema (automática).

### Período activo (R-PER-01)

El período lectivo vigente se resuelve por regla de negocio, nunca como una constante fija en el código.

---

## 7. Decisiones institucionales pendientes

Estas decisiones afectan la integración con otros módulos y no pueden resolverse solo por el equipo de desarrollo:

| ID | Tema | Impacto |
| :--- | :--- | :--- |
| **DEC-017** | ¿Dónde se persiste oficialmente la asistencia? | Escenario A: el módulo central la almacena. Escenario B: el Sistema Profesor la almacena y sincroniza. |
| **DEC-016/028** | ¿Qué protocolo de autenticación se usa? | Actualmente se simula con `X-Profesor-Id`. No es seguro para producción. |
| **DEC-018** | ¿Cómo se obtienen los datos maestros? | ¿Consulta en tiempo real al SGA, réplica local, claims en el token? |
| **DEC-021** | ¿Se permite rectificar asistencia en el día? | Afecta si la asistencia es de solo lectura inmediatamente o tiene una ventana de edición. |

El detalle completo está en [DECISIONS.md §5](../DECISIONS.md).

---

## 8. Estado actual de las funcionalidades

### Backend (Django 5.2 + DRF)

- 9 modelos de dominio implementados y migrados.
- API REST con autorización Zero Trust por scope docente.
- 40 pruebas automatizadas pasando al 100% (`pytest`).
- Linter `ruff` con 0 errores.
- Documentación Swagger UI en `/api/docs/`.

### Frontend (React 19 + TypeScript + Vite)

- Interfaz funcional completa para las 5 vistas del MVP (comisiones, nómina, asistencia, observaciones, perfil).
- Rediseño visual con paleta institucional.
- Accesibilidad WCAG 2.1 AA (navegación por teclado, contraste, ARIA).
- Compilación y linter con 0 errores (`tsc`, `oxlint`).

### Endpoints principales

| Endpoint | Método | Funcionalidad |
| :--- | :--- | :--- |
| `/api/health/` | GET | Verificación de salud del backend |
| `/api/profesores/` | GET | Catálogo de profesores (modo desarrollo) |
| `/api/profesor/perfil/` | GET | Perfil del docente autenticado |
| `/api/profesor/comisiones/` | GET | Comisiones asignadas al docente |
| `/api/comisiones/{id}/alumnos/` | GET | Nómina de estudiantes de una comisión |
| `/api/comisiones/{id}/clases/` | GET/POST | Instancias de clase de una comisión |
| `/api/comisiones/{id}/clases/{id}/asistencia/validar/` | POST | Validación de lote de asistencia |
| `/api/comisiones/{id}/observaciones/` | GET/POST | Observaciones académicas |
| `/api/docs/` | GET | Documentación Swagger UI |
| `/api/schema/` | GET | Esquema OpenAPI 3.0 |

### Pruebas existentes

| Archivo | Cantidad | Cobertura |
| :--- | :--- | :--- |
| `tests/test_health.py` | 4 | Verificación de salud y esquema OpenAPI |
| `tests/test_domain_models.py` | ~12 | Modelos de dominio, validaciones e invariantes |
| `tests/test_api.py` | ~12 | Endpoints REST, scope docente y flujo completo |
| `tests/test_security_robustness.py` | 12 | Blindaje de parámetros, cuerpos inválidos y suplantación |
| **Total** | **40** | Todas pasando al 100% |
