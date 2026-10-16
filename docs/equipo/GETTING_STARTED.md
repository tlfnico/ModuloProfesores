# Guía de Inicio — Preparar el entorno local en Windows

**Proyecto:** SGA — Sistema Profesor  
**Última actualización:** 2026-10-16  
**Documentos relacionados:** [HANDBOOK.md](./HANDBOOK.md) | [backend/README.md](../../backend/README.md) | [frontend/README.md](../../frontend/README.md)

---

## Requisitos previos

Antes de empezar, asegurate de tener instalado:

| Herramienta | Versión mínima | ¿Para qué? |
| :--- | :--- | :--- |
| **Python** | 3.12+ | Backend Django |
| **Node.js** | 20 LTS o superior | Frontend React + Vite |
| **npm** | 10+ (viene con Node) | Gestor de paquetes del frontend |
| **PostgreSQL** | 16+ | Base de datos (opcional para desarrollo: SQLite como alternativa) |
| **Git** | 2.40+ | Control de versiones |

> **Tip:** Podés verificar las versiones con:
> ```powershell
> python --version
> node --version
> npm --version
> psql --version
> git --version
> ```

---

## 1. Clonar el repositorio

```powershell
git clone <URL-del-repositorio>
cd <nombre-del-repositorio>
```

La estructura que vas a ver es:

```
├── backend/        # API Django + DRF
├── frontend/       # Interfaz React + TypeScript + Vite
├── docs/           # Documentación técnica y de equipo
├── spec.md         # Especificación técnica original
└── .gitignore
```

---

## 2. Configurar el backend

### 2.1. Crear el entorno virtual de Python

```powershell
cd backend
py -3 -m venv .venv
```

### 2.2. Activar el entorno virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

> Si PowerShell bloquea la ejecución de scripts, ejecutá antes:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

### 2.3. Instalar dependencias

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Las dependencias principales son:

| Paquete | Versión | Propósito |
| :--- | :--- | :--- |
| Django | ≥5.2 | Framework web backend |
| djangorestframework | ≥3.16 | API REST |
| drf-spectacular | ≥0.28 | Documentación OpenAPI / Swagger |
| psycopg[binary] | ≥3.2 | Driver PostgreSQL |
| python-decouple | ≥3.8 | Variables de entorno |
| pytest / pytest-django | ≥8.0 / ≥4.9 | Pruebas automatizadas |
| ruff | ≥0.11 | Linter y formateador |

### 2.4. Configurar variables de entorno

```powershell
Copy-Item .env.example .env
```

Abrí el archivo `.env` y ajustá los valores según tu entorno local:

```ini
SECRET_KEY=django-insecure-dev-only-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos
DB_ENGINE=django.db.backends.postgresql
DB_NAME=sga_profesor
DB_USER=postgres
DB_PASSWORD=<tu-contraseña-local>
DB_HOST=localhost
DB_PORT=5432
```

> **⚠️ Importante:** No subas tu archivo `.env` al repositorio. Está en `.gitignore`.

#### Si no tenés PostgreSQL instalado

Podés usar SQLite temporalmente para desarrollo cambiando el motor en `.env`:

```ini
DB_ENGINE=django.db.backends.sqlite3
```

El resto de las variables de base de datos se ignoran con SQLite.

### 2.5. Crear la base de datos en PostgreSQL (si usás PostgreSQL)

```powershell
psql -U postgres
```

```sql
CREATE DATABASE sga_profesor;
\q
```

### 2.6. Verificar la configuración y ejecutar migraciones

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py migrate
```

### 2.7. Cargar datos de demostración

El proyecto incluye un comando para poblar la base con datos de ejemplo (profesores, comisiones, materias, alumnos):

```powershell
.\.venv\Scripts\python.exe manage.py seed_demo_data
```

### 2.8. Ejecutar el servidor de desarrollo

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Verificá que funcione abriendo en el navegador:

- **Salud:** http://127.0.0.1:8000/api/health/
- **Swagger UI:** http://127.0.0.1:8000/api/docs/

### 2.9. Ejecutar pruebas del backend

```powershell
# Pruebas automatizadas
.\.venv\Scripts\pytest.exe

# Linter
.\.venv\Scripts\ruff.exe check .
```

Las 40 pruebas deberían pasar al 100%.

---

## 3. Configurar el frontend

### 3.1. Instalar dependencias

```powershell
cd ..\frontend
npm install
```

### 3.2. Configurar variables de entorno

```powershell
Copy-Item .env.example .env
```

El contenido por defecto apunta al backend local:

```ini
VITE_API_URL=http://localhost:8000/api
```

> **Nota:** El frontend usa un proxy en Vite que redirige `/api` al backend en `http://127.0.0.1:8000`, así que en la práctica no necesitás modificar este valor para desarrollo local.

### 3.3. Ejecutar el servidor de desarrollo

```powershell
npm run dev
```

La aplicación estará en **http://localhost:5173**.

> **Importante:** Para que el frontend funcione correctamente, el backend tiene que estar corriendo en otra terminal (paso 2.8).

### 3.4. Verificar compilación y calidad

```powershell
# Compilación TypeScript + Vite build
npm run build

# Linter
npm run lint
```

---

## 4. Resumen: dos terminales

Para trabajar, necesitás dos terminales abiertas:

| Terminal | Directorio | Comando |
| :--- | :--- | :--- |
| **Terminal 1** (Backend) | `backend/` | `.\.venv\Scripts\python.exe manage.py runserver` |
| **Terminal 2** (Frontend) | `frontend/` | `npm run dev` |

---

## 5. Solución de errores frecuentes

### "ModuleNotFoundError" al ejecutar manage.py

→ Verificá que el entorno virtual esté activado (`.\.venv\Scripts\Activate.ps1`) o usá la ruta completa al intérprete (`.\.venv\Scripts\python.exe`).

### "FATAL: database sga_profesor does not exist"

→ Creá la base de datos en PostgreSQL (`CREATE DATABASE sga_profesor;`) o cambiá a SQLite en `.env`.

### "FATAL: password authentication failed for user postgres"

→ Verificá la contraseña de PostgreSQL en tu `.env`. La contraseña es la que configuraste al instalar PostgreSQL.

### "PowerShell no permite ejecutar scripts"

→ Ejecutá: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

### El frontend muestra errores de conexión a la API

→ Verificá que el backend esté corriendo en `http://127.0.0.1:8000`. El proxy de Vite redirige las peticiones `/api` a esa dirección.

### "npm run build" falla con errores de TypeScript

→ Asegurate de tener Node.js 20+ y ejecutá `npm install` antes del build.

### Las pruebas del backend fallan con errores de base de datos

→ Si estás usando PostgreSQL, verificá que la base de datos exista y las credenciales sean correctas. Si querés pruebas sin PostgreSQL, usá `DB_ENGINE=django.db.backends.sqlite3` en `.env`.

---

## 6. Estructura de archivos importante

```
backend/
├── apps/core/                # Núcleo del módulo profesor
│   ├── models.py             # 9 modelos de dominio
│   ├── domain/
│   │   ├── ports.py          # Interfaces abstractas (puertos hexagonales)
│   │   └── attendance.py     # Lógica de validación de asistencia
│   ├── api/
│   │   ├── views.py          # Vistas REST
│   │   ├── serializers.py    # Serialización de datos
│   │   └── urls.py           # Rutas de la API
│   └── management/           # Comandos personalizados (seed_demo_data)
├── config/
│   ├── settings.py           # Configuración Django (usa python-decouple)
│   └── urls.py               # Rutas raíz
└── tests/                    # 40 pruebas automatizadas

frontend/
├── src/
│   ├── App.tsx               # Componente principal con navegación por pestañas
│   ├── api/client.ts         # Cliente HTTP para la API
│   ├── components/           # 7 componentes de interfaz
│   ├── types/                # Tipos TypeScript
│   └── index.css             # Sistema de estilos (WCAG 2.1 AA)
└── vite.config.ts            # Proxy hacia el backend
```

---

## 7. Siguientes pasos

Una vez que tengas el entorno funcionando:

1. Leé el [HANDBOOK.md](./HANDBOOK.md) para entender el sistema.
2. Consultá [MODULES_AND_INTEGRATION.md](./MODULES_AND_INTEGRATION.md) si vas a trabajar en integración.
3. Seguí las convenciones de [TEAM_WORKFLOW.md](./TEAM_WORKFLOW.md) para colaborar.
4. Revisá el [PROGRESS.md](../PROGRESS.md) para ver qué está hecho y qué falta.
