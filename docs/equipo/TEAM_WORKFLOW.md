# Guía de Trabajo en Equipo y Buenas Prácticas (TEAM_WORKFLOW)

**Proyecto:** Sistema de Gestión Académica (SGA) — Monolito Modular  
**Última actualización:** 2026-10-16  
**Documentos relacionados:** [README.md](./README.md) | [HANDBOOK.md](./HANDBOOK.md) | [MODULES_AND_INTEGRATION.md](./MODULES_AND_INTEGRATION.md) | [GETTING_STARTED.md](./GETTING_STARTED.md) | [DECISIONS.md](../DECISIONS.md)

---

## 1. Introducción y Filosofía de Trabajo

El Sistema de Gestión Académica (SGA) está concebido como un **monolito modular**. Esto significa que todos los módulos (Profesor, Preceptor, etc.) comparten un mismo repositorio y una misma base tecnológica (Django + React), pero mantienen sus dominios y responsabilidades delimitados para que varios desarrolladores puedan trabajar en paralelo sin pisarse.

### Principios rectores del equipo

1. **Claridad y simplicidad:** Preferimos código legible y explícito por sobre soluciones complejas o "mágicas". El proyecto debe ser comprensible para cualquier compañero que se sume.
2. **Accesibilidad como requisito (no opcional):** Nuestro sistema sirve a docentes, preceptores, familias y personas con discapacidad. Toda interfaz debe ser accesible (teclado, contraste suficiente, lectores de pantalla, semántica HTML).
3. **Seguridad Zero Trust:** Todo dato ingresado por el usuario se considera no confiable. Las validaciones se ejecutan siempre en el servidor.
4. **Respeto a los contratos compartidos:** Antes de modificar un modelo o endpoint compartido, se conversa con el equipo y se registra la decisión en [DECISIONS.md](../DECISIONS.md).

---

## 2. Flujo de Git y Gestión de Ramas

Para mantener la estabilidad de la rama principal (`main`), seguimos una estrategia de **Feature Branches** (ramas por funcionalidad o tarea).

```
main ──────────●───────────────────────●────────── (siempre estable y funcional)
                \                     /
feature/xxx      ●─────────●─────────● (trabajo aislado del integrante)
```

### 2.1. Nombres de ramas recomendados

Utilizamos prefijos claros según el tipo de cambio:

- `feature/profesor-asistencia-ui`: Nueva funcionalidad en el módulo profesor.
- `feature/preceptor-parte-diario`: Nueva funcionalidad en el módulo preceptor.
- `fix/error-calculo-asistencia`: Corrección de un bug.
- `docs/guia-trabajo-equipo`: Mejoras o adiciones a la documentación.
- `refactor/puerto-notificaciones`: Refactorización de código sin cambio de comportamiento.

### 2.2. Convención de mensajes de commit (Conventional Commits)

Cada commit debe ser atómico (hacer una sola cosa bien) y tener un mensaje descriptivo:

```
<tipo>(<alcance>): <descripción breve en imperativo>

[cuerpo explicativo opcional]
```

**Tipos permitidos:**
- `feat`: Nueva característica para el usuario (ej. `feat(profesor): agregar validación de estado de asistencia`).
- `fix`: Corrección de un defecto (ej. `fix(core): corregir filtro de comisiones por período activo`).
- `docs`: Cambios únicamente en documentación (ej. `docs(equipo): actualizar guía de inicio rápido`).
- `test`: Añadir o modificar pruebas automatizadas (ej. `test(profesor): añadir prueba de idempotencia en toma de asistencia`).
- `refactor`: Cambio de código que no añade funcionalidad ni corrige un bug (ej. `refactor(api): extraer serializador a módulo independiente`).
- `style`: Formato de código, punto y coma, orden de imports (sin cambio lógico).
- `chore`: Tareas de mantenimiento de configuración o dependencias.

> **Importante:** En este repositorio las operaciones de Git y commits definitivos en ramas compartidas son coordinados por el responsable del proyecto.

---

## 3. Políticas de Base de Datos y Migraciones

La base de datos es el punto de contacto más delicado en un monolito modular. Seguir estas reglas evita inconsistencias y migraciones rotas entre compañeros.

### 3.1. Regla de oro de las migraciones

> ⚠️ **NUNCA modifiques ni borres un archivo de migración que ya haya sido integrado a la rama principal (`main`) o compartido con otro compañero.**

Si necesitas cambiar un campo o modelo:
1. Modifica el archivo `models.py`.
2. Genera una **nueva** migración con `python manage.py makemigrations`.
3. Aplica la migración con `python manage.py migrate`.

### 3.2. Convivencia entre módulos en `apps.core`

- **Entidades maestras (`Profesor`, `Alumno`, `Comision`, `Materia`, etc.):** Son compartidas. Si necesitas agregar un campo a una entidad maestra, **debes avisar primero al equipo** para asegurar que no afecte las vistas o supuestos de otros módulos.
- **Entidades propias:** Cada módulo puede crear sus modelos específicos (ej. `InstanciaClase` u `ObservacionAcademica` para Profesor; `ParteDiario` o `RetiroAnticipado` para Preceptor).
- **No duplicar conceptos:** Si una entidad ya existe en el modelo de dominio ([SPEC-002](../specs/SPEC-002-modelo-dominio.md)), reutilízala a través de claves foráneas en lugar de crear tablas paralelas con información redundante.

### 3.3. Entorno de Base de Datos: Dualidad SQLite / PostgreSQL

Para garantizar que cualquier compañero pueda programar sin trabas de instalación:
- El proyecto soporta **PostgreSQL 18** (producción y staging recomendado).
- El proyecto soporta **SQLite local** si no tienes PostgreSQL instalado (mediante configuración en `.env`, ver [GETTING_STARTED.md](./GETTING_STARTED.md)).
- Las pruebas automáticas de pytest corren de forma aislada y rápida en SQLite en memoria.

---

## 4. Estándares de Código y Calidad

Para mantener una base de código limpia y homogénea, usamos linters y formateadores automáticos en backend y frontend.

### 4.1. Backend (Python & Django)

- **Guía de estilo:** PEP 8.
- **Linter y formateador:** `ruff`.
  ```bash
  # Ejecutar ruff para verificar el código
  ruff check .

  # Corregir automáticamente problemas de formato
  ruff check --fix .
  ```
- **Tipado estricto:** Usar Type Hints en funciones de servicios, lógica de dominio y puertos:
  ```python
  def validar_estado_asistencia(estado: str) -> bool:
      ...
  ```
- **Manejo de errores:** No silenciar excepciones con `except: pass`. Usar excepciones específicas y respuestas HTTP semánticas (`400 Bad Request`, `403 Forbidden`, `404 Not Found`).

### 4.2. Frontend (React 19 + TypeScript + Vite)

- **TypeScript estricto:** No usar `any` sin justificación documentada. Definir interfaces para los modelos de datos y respuestas de la API.
- **Linter:** `oxlint` y `eslint`.
  ```bash
  npm run lint
  ```
- **Verificación de tipos:** Antes de dar por terminada una tarea, verificar que TypeScript compile sin errores:
  ```bash
  npm run build
  ```
- **Componentes desacoplados:** Separar la lógica de llamada a la API (`api/`) de la capa de componentes visuales (`components/`).

---

## 5. Accesibilidad (WCAG 2.1 AA)

La accesibilidad es un **requisito no negociable** en este proyecto. Todo nuevo componente visual debe contemplar:

1. **Navegación por teclado completa:**
   - Todos los botones, enlaces y campos de formulario deben ser alcanzables mediante la tecla `Tab`.
   - Se debe poder accionar elementos interactivos con `Enter` y `Espacio`.
   - El foco visible (`:focus-visible`) nunca debe ser eliminado con `outline: none` sin un reemplazo visual claro.
2. **HTML semántico:**
   - Usar `<button>` para acciones y `<a>` para navegación.
   - Usar elementos de encabezado ordenados (`<h1>`, luego `<h2>`, `<h3>`).
   - Los campos de formulario deben tener siempre su etiqueta `<label htmlFor="...">` asociada.
3. **Contraste de colores:**
   - Proporción mínima de contraste 4.5:1 para texto normal y 3:1 para texto grande o elementos gráficos interactivos.
4. **Mensajes para lectores de pantalla:**
   - Los estados de carga deben comunicarse (ej. `aria-busy="true"`, `role="status"`).
   - Los iconos sin texto deben tener `aria-label` o `aria-hidden="true"` si son meramente decorativos.
5. **Diseño responsivo y amigable para móviles:**
   - El sistema debe funcionar en pantallas táctiles de celulares (área táctil mínima de 44x44px en botones).

---

## 6. Seguridad y Validación

1. **Validación en Backend:** Nunca confíes únicamente en la validación del frontend. El backend debe validar tipos, formatos, longitudes y reglas de negocio.
2. **Autorización y Scope (Zero Trust):**
   - No asumir que un usuario tiene acceso a un recurso por conocer su ID.
   - Siempre verificar pertenencia (ej. que la comisión pertenezca a la asignación del profesor autenticado antes de permitir registrar una observación o clase).
3. **Manejo de Secretos:**
   - Nunca incluir contraseñas, claves secretas (`SECRET_KEY`), ni credenciales en el código fuente.
   - Usar siempre variables de entorno en el archivo `.env` (el cual está en `.gitignore`).

---

## 7. Verificación Local Antes de Compartir Cambios

Antes de solicitar una revisión o merge a la rama compartida, el desarrollador debe verificar localmente que todo el proyecto se encuentre en verde:

### Checklist de verificación local:

#### 1. Backend
- [ ] Las migraciones aplican limpiamente:
  ```bash
  python manage.py migrate
  ```
- [ ] La suite de pruebas pasa al 100%:
  ```bash
  pytest
  ```
- [ ] El linter no arroja errores:
  ```bash
  ruff check .
  ```

#### 2. Frontend
- [ ] Compilación TypeScript sin errores:
  ```bash
  npm run build
  ```
- [ ] Linter sin observaciones:
  ```bash
  npm run lint
  ```
- [ ] Navegación interactiva verificada con teclado en el navegador.

---

## 8. Canales de Coordinación y Resolución de Dudas

- **Dudas sobre el modelo de datos o reglas de negocio:** Consultar [SPEC-002](../specs/SPEC-002-modelo-dominio.md) y [HANDBOOK.md](./HANDBOOK.md).
- **Proponer cambios arquitectónicos o de integración:**
  1. Conversar con el equipo (Nicolás / responsable del módulo complementario).
  2. Redactar una propuesta breve en [DECISIONS.md](../DECISIONS.md) siguiendo el formato ADR (Contexto, Alternativas, Decisión y Consecuencias).
- **Reporte de bloqueos:** Si una tarea depende de una entidad o endpoint del otro módulo que aún no está listo, acordar un contrato mockeado provisorio según lo especificado en [MODULES_AND_INTEGRATION.md](./MODULES_AND_INTEGRATION.md#6-contratos-pendientes-y-acuerdos-requeridos).
