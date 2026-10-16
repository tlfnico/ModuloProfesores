# SPEC-001 — Inicialización del Sistema Profesor

**Estado:** Propuesta técnica inicial  
**Proyecto:** Sistema de Gestión Académica — Sistema Profesor  
**Versión:** 1.0  
**Alcance:** Arquitectura base y preparación del entorno. No implementar todavía las funcionalidades del MVP.

## 1. Objetivo técnico y alcance

Preparar la estructura inicial de un sistema web que permita a los profesores consultar sus comisiones y materias, gestionar la toma de asistencia y registrar observaciones académicas por alumno.

El proyecto comienza desde cero. No se debe asumir que existen código fuente, modelos de datos, endpoints o servicios disponibles dentro del espacio de trabajo.

### Funcionalidades contempladas para el MVP

1. Acceso del profesor mediante el sistema de autenticación acordado.
2. Consulta de comisiones y materias asignadas durante el período actual.
3. Consulta de alumnos de una comisión.
4. Toma de asistencia con estados presente, ausente y tarde.
5. Consulta del historial de asistencia de alumnos.
6. Registro de observaciones académicas por alumno, comisión y fecha.

Las calificaciones numéricas, los comunicados y los archivos adjuntos quedan fuera del MVP y se documentarán como posibles funcionalidades futuras.

## 2. Arquitectura propuesta

Proponer una aplicación web con frontend y backend separados por una API REST.

- **Frontend:** React con TypeScript.
- **Backend:** Python con Django y Django REST Framework.
- **Base de datos:** PostgreSQL.
- **Contrato de API:** OpenAPI.
- **Control de versiones:** Git.
- **Pruebas:** pytest, junto con las herramientas de pruebas compatibles con Django y React.
- **Entorno reproducible:** Docker, si resulta conveniente para el equipo y el entorno de despliegue.

La arquitectura interna del backend será modular, con responsabilidades separadas por dominio. No implementar microservicios ni infraestructura distribuida sin una necesidad justificada.

### Principios arquitectónicos

- Separación entre presentación, reglas de negocio y persistencia.
- Responsabilidades claramente delimitadas.
- Validaciones en el backend; nunca confiar exclusivamente en el frontend.
- Interfaces explícitas entre módulos.
- Pruebas automatizadas para las reglas de negocio críticas.
- Configuración sensible mediante variables de entorno.
- Documentación de decisiones arquitectónicas y de integración.

## 3. Entidades e interfaces conceptuales

El siguiente modelo es preliminar y no representa todavía el esquema definitivo de la base de datos.

- **Usuario:** identidad autenticada y rol del usuario.
- **Profesor:** identidad docente asociada a uno o más vínculos académicos.
- **Alumno:** estudiante perteneciente a una comisión.
- **Comisión:** grupo académico al que se asignan alumnos y profesores.
- **Materia:** espacio curricular asociado a una comisión.
- **DocenteComision:** asignación de un profesor a una comisión y, cuando corresponda, a una materia.
- **Asistencia:** registro de asistencia de un alumno para una fecha e instancia de clase.
- **RegistroAcademico:** observación de texto libre asociada a un alumno, comisión y fecha.

Antes de crear las tablas, definir las cardinalidades, las claves, las restricciones de integridad y la responsabilidad de cada entidad.

No duplicar entidades de otros sistemas sin justificarlo. Determinar si los datos académicos serán propios del Sistema Profesor o se consultarán a través de APIs externas.

### Reglas preliminares

- Un profesor solo puede consultar las comisiones que tiene asignadas.
- La toma de asistencia debe limitarse a las comisiones autorizadas.
- El historial de asistencia será de solo lectura para el profesor.
- Los estados de asistencia admitidos serán presente, ausente y tarde.
- Una observación debe tener alumno, comisión, fecha y contenido válido.
- El período académico actual debe resolverse mediante una regla explícita, no mediante una fecha arbitraria codificada en el sistema.

## 4. Contratos de API e integración

Diseñar los contratos de API antes de implementar los endpoints definitivos.

Como propuesta inicial, evaluar los siguientes recursos:

- `GET /api/v1/docente/comisiones/`
- `GET /api/v1/comisiones/{id}/alumnos/`
- `GET /api/v1/comisiones/{id}/asistencias/`
- `POST /api/v1/comisiones/{id}/asistencias/`
- `GET /api/v1/alumnos/{id}/asistencias/`
- `GET /api/v1/comisiones/{id}/observaciones/`
- `POST /api/v1/comisiones/{id}/observaciones/`

Estos endpoints son candidatos para discusión, no contratos aprobados. No implementarlos hasta documentar sus parámetros, respuestas, validaciones, errores y permisos.

### Integración con autenticación y asistencia

El alcance académico indica que existen módulos de autenticación y asistencia, pero sus implementaciones y contratos todavía no están disponibles en esta etapa.

Por lo tanto:

- No construir un sistema de autenticación paralelo como solución definitiva.
- No duplicar el sistema de asistencia existente.
- Definir qué información y operaciones proporcionará cada módulo.
- Establecer cómo se identificarán usuarios, profesores, alumnos y comisiones entre sistemas.
- Documentar si la integración será por API HTTP o mediante componentes de una aplicación compartida.
- Si se necesita avanzar antes de alcanzar un acuerdo, utilizar interfaces provisionales claramente identificadas y reemplazables.

La autenticación identifica al usuario; la autorización debe verificar también que tenga acceso a la comisión y al recurso solicitados.

## 5. Criterios de aceptación

La inicialización se considerará completa cuando:

1. La estructura propuesta esté documentada y sea coherente con el alcance del MVP.
2. Las responsabilidades del frontend, backend y base de datos estén delimitadas.
3. Se haya definido una organización modular del backend.
4. Las decisiones pendientes de integración estén registradas explícitamente.
5. No existan dependencias ficticias de servicios externos ni endpoints inventados como si estuvieran confirmados.
6. La configuración permita ejecutar el proyecto en un entorno de desarrollo reproducible.
7. Se documenten los comandos de instalación, ejecución y pruebas.
8. La aplicación pueda comprobarse mediante verificaciones básicas de salud y una prueba inicial automatizada.
9. No se implementen funcionalidades del MVP antes de aprobar el diseño de dominio y los contratos necesarios.

## 6. Plan de implementación

### Etapa 1 — Inspección y planificación
- Inspeccionar el espacio de trabajo y comprobar si está vacío.
- Identificar restricciones técnicas o archivos existentes.
- Presentar la estructura de directorios propuesta.
- Registrar decisiones y preguntas abiertas.

### Etapa 2 — Preparación del entorno
- Configurar frontend, backend y PostgreSQL.
- Establecer variables de entorno y archivos de ejemplo sin credenciales reales.
- Preparar herramientas de formato, análisis estático y pruebas.
- Documentar la ejecución local.

### Etapa 3 — Estructura arquitectónica
- Delimitar los módulos de dominio.
- Establecer convenciones de nombres, configuración y manejo de errores.
- Preparar el mecanismo de documentación OpenAPI.
- No crear modelos definitivos hasta revisar el diseño conceptual.

### Etapa 4 — Validación
- Ejecutar las verificaciones de instalación y compilación correspondientes.
- Ejecutar las pruebas iniciales.
- Informar archivos creados, decisiones tomadas, resultados y problemas pendientes.

## 7. Instrucciones para Antigravity

Actuar como ingeniero de software responsable de ejecutar esta especificación.

No asumir decisiones que todavía no fueron acordadas. Cuando falte información que afecte la arquitectura, la seguridad, la integridad de los datos o la integración entre módulos, documentar la cuestión y presentar alternativas.

Antes de realizar cada cambio relevante, explicar qué se modificará y por qué. No avanzar a la siguiente funcionalidad del MVP hasta que se apruebe su especificación técnica correspondiente.

Al finalizar, entregar un resumen de lo implementado, las verificaciones ejecutadas y las decisiones pendientes para la siguiente etapa.