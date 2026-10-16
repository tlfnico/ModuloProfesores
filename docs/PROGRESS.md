# Estado de Avance del Proyecto (PROGRESS)

**Proyecto:** Sistema de Gestión Académica — Sistema Profesor  
**Última actualización:** 2026-10-16 (Sesión 1 — Dominio y Modelos Base)  
**Responsable técnico:** Ingeniero / Arquitecto de Software Senior (Antigravity)

---

## 1. Resumen Ejecutivo

- **Estado general:** Modelos de dominio y reglas de negocio base implementados, migrados y testeados con éxito. Se implementaron las entidades académicas maestras (`PeriodoLectivo`, `Profesor`, `Materia`, `Comision`, `AsignacionDocente`, `Alumno`, `VinculoAlumnoComision`) y los conceptos propios del Módulo Profesor (`InstanciaClase` con identidad propia para múltiples sesiones por día, y `ObservacionAcademica` con doble marca de tiempo). Se implementaron los servicios y validaciones de dominio de Asistencia (`EstadoAsistencia`, tomas parciales R-ASI-02 e idempotencia) manteniendo la persistencia oficial de asistencia desacoplada de acuerdo a DEC-017.
- **Etapa activa:** **Etapa 6 — Implementación Incremental del MVP (Bloque 2 / Sesión 1)**
- **Estado de dependencias y código:**
  - **Backend:** Migración `0001_initial` aplicada en `apps.core`. Endpoints REST con Scope Docente Zero Trust (`/api/profesor/comisiones/`, `/api/comisiones/{id}/alumnos/`, `/api/comisiones/{id}/clases/`, `/api/comisiones/{id}/observaciones/`) en vivo. Suite automatizada ampliada a **24 pruebas pasando al 100% en pytest**. Linter `ruff` con 0 errores.
  - **Frontend:** Proyecto React 19 + TypeScript con Vite. Compilación (`tsc` + Vite build) y linter (`oxlint`) con 0 errores.
  - **Base de datos:** Configurada mediante `python-decouple` con soporte dual para PostgreSQL 18 y SQLite local para pruebas automatizadas.
  - **Operaciones Git:** Cero comandos Git ejecutados y cero commits realizados (reservado exclusivamente para el responsable del proyecto).

---

## 2. Historial de Tareas y Estado

| Tarea | Descripción | Estado | Fecha |
| :--- | :--- | :--- | :--- |
| **Tarea 0.1** | Inspección inicial y planificación del proyecto | **Completada** | 2026-10-15 |
| **Tarea 1.1** | Evaluación de arquitectura e integración | **Completada** | 2026-10-15 |
| **Tarea 1.2** | Revisión crítica y cierre de la propuesta arquitectónica | **Completada** | 2026-10-15 |
| **Tarea 2.1** | **Diseño conceptual del dominio del Sistema Profesor** | **Completada** | 2026-10-15 |
| - *Subtareas 2.1* | Entidades, relaciones, reglas de negocio, escenarios límite, SPEC-002 v1.0 | Completada | 2026-10-15 |
| **Tarea 2.2** | **Correcciones finales del modelo de dominio** | **Completada** | 2026-10-15 |
| **Tarea 2.3** | **Evaluación técnica del entorno y diagnóstico de base** | **Completada** | 2026-10-16 |
| **Tarea 2.4** | **Preparación de la estructura base del proyecto** | **Completada** | 2026-10-16 |
| **Bloque 1 (Etapa 5)** | **Diseño técnico e inicialización del proyecto (Scaffolding)** | **Completada** | 2026-10-16 |
| **Sesión 1 (Etapa 6)** | **Desarrollo del dominio y modelos base del Módulo Profesor** | **Completada** | 2026-10-16 |
| - *Modelos base* | 9 modelos creados en `apps/core/models.py` con invariantes y métodos de negocio. | Completada | 2026-10-16 |
| - *Migración inicial* | Migración `0001_initial` creada y aplicada en la base de datos. | Completada | 2026-10-16 |
| - *Reglas de asistencia* | Enumeración cerrada (`PRESENTE`, `AUSENTE`, `TARDE`), tomas parciales válidas (R-ASI-02) y servicio de validación en `domain/attendance.py`. | Completada | 2026-10-16 |
| - *Endpoints y Scope* | Vistas REST con autorización Zero Trust para comisiones (F1), nómina (F2), clases y observaciones (F5). | Completada | 2026-10-16 |
| - *Pruebas unitarias* | Suite ampliada a 24 tests automatizados pasando en verde en pytest. | Completada | 2026-10-16 |
| - *Persistencia Asistencia* | **DEC-017 se mantiene formalmente como cuestión institucional abierta** (sin forzar segunda fuente oficial). | Registrada | 2026-10-16 |
| **Etapa 6 (Sesión 2)** | Integración de interfaces frontend para consulta de comisiones, nómina y observaciones | **Próxima a iniciar** | — |
| **Etapa 7** | Integración, pruebas y validación final | Bloqueada / No autorizada | — |

---

## 3. Entregables Generados (Bloque 1)

1. **Backend inicializado (`backend/`):**
   - Entorno virtual `.venv` con dependencias instaladas.
   - Configuración Django desacoplada (`config/settings.py`, `config/urls.py`, `pyproject.toml`, `.env.example`).
   - Puertos hexagonales abstractos ([`backend/apps/core/domain/ports.py`](file:///c:/Users/Nicolas/Desktop/tarea/backend/apps/core/domain/ports.py)).
   - Endpoints de verificación de salud y documentación Swagger UI / OpenAPI 3.0.
   - Suite de pruebas automatizadas ([`backend/tests/test_health.py`](file:///c:/Users/Nicolas/Desktop/tarea/backend/tests/test_health.py)).
   - Documentación técnica y comandos de ejecución ([`backend/README.md`](file:///c:/Users/Nicolas/Desktop/tarea/backend/README.md)).
2. **Frontend inicializado (`frontend/`):**
   - Proyecto React 19 + TypeScript con Vite.
   - Cliente HTTP para comprobación de salud ([`frontend/src/api/client.ts`](file:///c:/Users/Nicolas/Desktop/tarea/frontend/src/api/client.ts)).
   - Componentes semánticos y accesibles ([`Header.tsx`](file:///c:/Users/Nicolas/Desktop/tarea/frontend/src/components/Header.tsx), [`StatusCard.tsx`](file:///c:/Users/Nicolas/Desktop/tarea/frontend/src/components/StatusCard.tsx), [`App.tsx`](file:///c:/Users/Nicolas/Desktop/tarea/frontend/src/App.tsx)).
   - Hoja de estilos accesible WCAG 2.1 AA ([`frontend/src/index.css`](file:///c:/Users/Nicolas/Desktop/tarea/frontend/src/index.css)).
   - Configuración de entorno ([`frontend/.env.example`](file:///c:/Users/Nicolas/Desktop/tarea/frontend/.env.example)).
   - Documentación y principios de accesibilidad ([`frontend/README.md`](file:///c:/Users/Nicolas/Desktop/tarea/frontend/README.md)).
3. **Documentación de Arquitectura y Decisiones:**
   - [`docs/DECISIONS.md`](file:///c:/Users/Nicolas/Desktop/tarea/docs/DECISIONS.md): Decisiones técnicas de stack y arquitectura adoptadas en Bloque 1.
   - [`docs/ARCHITECTURE.md`](file:///c:/Users/Nicolas/Desktop/tarea/docs/ARCHITECTURE.md): Estado actualizado con la base técnica inicializada.
   - [`docs/ROADMAP.md`](file:///c:/Users/Nicolas/Desktop/tarea/docs/ROADMAP.md): Etapa 5 cerrada; Etapa 6 posicionada como próximo bloque.

---

---

## 4. Sesión 1 y Sesión 2 — Dominio, Backend REST e Interfaz Funcional del Profesor (Completadas)

### 4.1 Dominio y Backend REST (Sesión 1)
- **Modelos y Persistencia:** Implementados en [`backend/apps/core/models.py`](file:///c:/Users/Nicolas/Desktop/tarea/backend/apps/core/models.py): `PeriodoLectivo`, `Profesor`, `Materia`, `Comision`, `AsignacionDocente`, `Alumno`, `VinculoAlumnoComision`, `InstanciaClase` (soporta múltiples sesiones en el mismo día, R-CLS-01), `ObservacionAcademica` (doble fecha, R-OBS-04), y estados cerrados de asistencia `EstadoAsistencia` (`PRESENTE`, `AUSENTE`, `TARDE`).
- **Lógica de Negocio y Scope Docente:** Implementados en [`backend/apps/core/domain/attendance.py`](file:///c:/Users/Nicolas/Desktop/tarea/backend/apps/core/domain/attendance.py) y validaciones en modelos (autorización estricta de alcance docente Zero Trust, R-DOC-01; soporte de toma parcial R-ASI-02; consistencia temporal de cursadas).
- **API REST y Contratos:** Endpoints para catálogo docente provisional, perfil, comisiones asignadas, nómina de comisión, clases, validación de lote de asistencia con métricas, y observaciones.
- **Pruebas Automatizadas:** 28 pruebas unitarias y de integración pasando al 100% en `pytest` (`backend/tests/`).
- **Datos de Demostración:** Comando `seed_demo_data` creado para poblar períodos, profesores, comisiones, materias, alumnos y clases para evaluación de desarrollo.

### 4.2 Interfaz Funcional del Profesor (Sesión 2)
- **Capa de Servicios Centralizada:** [`frontend/src/api/client.ts`](file:///c:/Users/Nicolas/Desktop/tarea/frontend/src/api/client.ts) conectada a la API mediante proxy Vite, inyectando la cabecera provisional `X-Profesor-Id`.
- **Selector de Perfil Docente:** [`ProfesorSelector.tsx`](file:///c:/Users/Nicolas/Desktop/tarea/frontend/src/components/ProfesorSelector.tsx) para alternar identidades docentes en entorno de desarrollo.
- **F1 — Comisiones Asignadas:** [`ComisionesList.tsx`](file:///c:/Users/Nicolas/Desktop/tarea/frontend/src/components/ComisionesList.tsx) con listado responsivo, período activo y materias asociadas.
- **F2 — Nómina de Estudiantes:** [`NominaTable.tsx`](file:///c:/Users/Nicolas/Desktop/tarea/frontend/src/components/NominaTable.tsx) con filtro en vivo por nombre/legajo/DNI, soporte de bajas (Escenario 2) y derivación directa a observaciones.
- **F3 / F4 — Asistencia Áulica:** [`AsistenciaAulica.tsx`](file:///c:/Users/Nicolas/Desktop/tarea/frontend/src/components/AsistenciaAulica.tsx) con gestión de instancias de clase, controles táctiles $\ge 44 \times 44\text{ px}$ accesibles para `[P]`, `[A]`, `[T]`, acciones rápidas, validación de lote en servidor y banner explicativo sobre el estado de DEC-017.
- **F5 — Observaciones Académicas:** [`ObservacionesPanel.tsx`](file:///c:/Users/Nicolas/Desktop/tarea/frontend/src/components/ObservacionesPanel.tsx) con selección de estudiante, doble marca temporal (hecho pedagógico vs registro del sistema), formulario accesible e historial.
- **Orquestación y Accesibilidad:** [`App.tsx`](file:///c:/Users/Nicolas/Desktop/tarea/frontend/src/App.tsx) y [`index.css`](file:///c:/Users/Nicolas/Desktop/tarea/frontend/src/index.css) con navegación por pestañas (`tablist`), foco visible `3px solid #025091`, enlaces de salto (`skip-link`), y conformidad WCAG 2.1 AA.
- **Verificación de Calidad:** Frontend validado con `oxlint` (0 advertencias, 0 errores) y `npm run build` (`tsc -b && vite build`) completado con éxito.

### 4.3 Robustecimiento, Seguridad Zero Trust y Verificación en Vivo
- **Blindaje de Parámetros de Consulta:** Validación de sintaxis UUID en `periodo_id` y `alumno_id` con fallback ordenado a códigos o legajos, evitando excepciones no controladas (500).
- **Protección contra Cuerpos Inválidos:** Manejo estricto de tipos de datos en endpoints `POST` para rechazar estructuras JSON inesperadas con 400 Bad Request.
- **Inmutabilidad de Autoría en Servidor:** Asignación forzada en servidor de `docente_registrador` y `autor` según el docente autenticado, impidiendo suplantaciones de identidad mediante manipulación de payloads.
- **Suite de Pruebas de Seguridad y Regresión:** Creada [`backend/tests/test_security_robustness.py`](file:///c:/Users/Nicolas/Desktop/tarea/backend/tests/test_security_robustness.py) con 12 pruebas automatizadas adicionales (totalizando 40 pruebas de backend aprobadas al 100%).
- **Comprobación de Integración en Vivo:** Ejecución exitosa de flujo completo contra el servidor en vivo en `http://127.0.0.1:8000/api` (catálogo, comisiones, nómina, clases, validación de lote de asistencia y notas pedagógicas).
- **Consistencia con DEC-017:** Confirmada la neutralidad de la interfaz respecto a la persistencia oficial; se informa exclusivamente la validación pedagógica sin alegar guardado permanente.

### 4.4 Rediseño Visual Institucional (Completado)
- **Paleta y Sistema de Diseño:** Aplicación rigurosa de la paleta institucional: azul institucional `#163A63`, blanco `#FFFFFF`, fondo canvas `#F3F5F8` y texto `#303846`, con bordes discretos `#D8DEE6` y sombras de elevación sutiles.
- **Estructura y Encabezado:** [`Header.tsx`](file:///c:/Users/Nicolas/Desktop/tarea/frontend/src/components/Header.tsx) con emblema institucional SVG, contexto del SGA y avatar circular del profesor activo. Barra de entorno de desarrollo ([`ProfesorSelector.tsx`](file:///c:/Users/Nicolas/Desktop/tarea/frontend/src/components/ProfesorSelector.tsx)) integrada de manera sobria y funcional.
- **Comisiones y Cursada (F1):** [`ComisionesList.tsx`](file:///c:/Users/Nicolas/Desktop/tarea/frontend/src/components/ComisionesList.tsx) con tarjetas de asignación modernas, chips de materias y estado activo destacado.
- **Nómina Profesional (F2):** [`NominaTable.tsx`](file:///c:/Users/Nicolas/Desktop/tarea/frontend/src/components/NominaTable.tsx) con buscador en tiempo real con icono, toggle switch accesible para alumnos dados de baja (Escenario 2), avatares con iniciales y códigos legajo destacados.
- **Toma de Asistencia Áulica (F3 / F4):** [`AsistenciaAulica.tsx`](file:///c:/Users/Nicolas/Desktop/tarea/frontend/src/components/AsistenciaAulica.tsx) con widget ribbon de métricas en vivo (Total, Presentes, Ausentes, Tardes, Sin Marcar), gestión ágil de clases, botones táctiles segmentados ($\ge 44 \times 44\text{ px}$) para `P`, `A`, `T` y banner institucional de DEC-017 de alta legibilidad.
- **Observaciones Pedagógicas (F5):** [`ObservacionesPanel.tsx`](file:///c:/Users/Nicolas/Desktop/tarea/frontend/src/components/ObservacionesPanel.tsx) en diseño balanceado de 2 columnas con formulario accesible y feed cronológico de notas con distinción entre hecho pedagógico y auditoría del sistema.
- **Accesibilidad y Calidad:** Mantenimiento estricto de WCAG 2.1 AA (foco visible `3px solid #163A63`, objetivos táctiles mínimos de 44px, enlaces de salto, atributos semánticos `tablist`/`tabpanel`).
- **Verificación Técnica:** `oxlint` (0 advertencias, 0 errores), `npm run build` completado en 232 ms y suite de 40 pruebas de backend aprobada al 100%.

---

## 5. Próximo Paso Recomendado

> Definir la resolución institucional sobre la propiedad de la persistencia de asistencia (DEC-017: Escenario A vs. Escenario B) para conectar la persistencia permanente oficial y formalizar el flujo de autenticación institucional de producción en reemplazo de la cabecera provisional `X-Profesor-Id`.



