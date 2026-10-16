# Backend — Sistema Profesor (SGA)

## 1. Estado Actual
**Base técnica inicial configurada y verificada (Bloque 1).**  
El backend cuenta con Django 5.2, Django REST Framework y drf-spectacular instalados en su entorno virtual local (`.venv`). Se dispone de comprobaciones de arranque, endpoint de salud `/api/health/`, documentación OpenAPI `/api/docs/` y suite de pruebas iniciales con `pytest` y `ruff`.

No se implementaron aún modelos de negocio ni lógica académica para respetar las decisiones institucionales abiertas.

---

## 2. Estructura de Directorios (Arquitectura Hexagonal / Puertos y Adaptadores)

```text
backend/
├── .env.example              # Plantilla de variables de entorno (sin secretos)
├── pyproject.toml            # Configuración de pytest y ruff
├── requirements.txt          # Dependencias mínimas fijadas
├── manage.py                 # Punto de entrada de gestión Django
├── config/                   # Configuración del proyecto Django
│   ├── settings.py           # Settings desacoplados con python-decouple
│   ├── urls.py               # Rutas raíz y endpoints /api/health/, /api/docs/
│   ├── wsgi.py
│   └── asgi.py
├── apps/                     # Aplicaciones y módulos del sistema
│   └── core/                 # Núcleo de arquitectura
│       ├── domain/           # Entidades puras y puertos abstractos
│       │   └── ports.py      # Interfaces IAuthenticationGateway, IAttendanceGateway, etc.
│       ├── application/      # Casos de uso y servicios de aplicación
│       ├── infrastructure/   # Adaptadores (PostgreSQL, gateways externos)
│       └── api/              # Controladores REST y serializadores
└── tests/                    # Suite de pruebas automatizadas
    └── test_health.py        # Pruebas de salud y generación OpenAPI
```

---

## 3. Comandos de Instalación, Ejecución y Pruebas

### 3.1. Preparación del Entorno Virtual e Instalación
```powershell
# En el directorio backend/
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3.2. Configuración de Variables de Entorno
Copiar el archivo de ejemplo y configurar las credenciales locales de PostgreSQL:
```powershell
Copy-Item .env.example .env
```
> **Nota:** Si PostgreSQL local aún no tiene base de datos o contraseña configurada, se puede definir temporalmente `DB_ENGINE=django.db.backends.sqlite3` en `.env` para pruebas aisladas de desarrollo.

### 3.3. Comprobación y Migraciones Base
```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py migrate
```

### 3.4. Ejecución del Servidor de Desarrollo
```powershell
.\.venv\Scripts\python.exe manage.py runserver
```
Endpoints disponibles:
- **Verificación de salud:** `http://127.0.0.1:8000/api/health/`
- **Documentación Swagger UI:** `http://127.0.0.1:8000/api/docs/`
- **Esquema OpenAPI (JSON/YAML):** `http://127.0.0.1:8000/api/schema/`

### 3.5. Pruebas y Calidad de Código
```powershell
# Ejecución de tests con pytest
.\.venv\Scripts\pytest.exe

# Análisis estático y formateo con ruff
.\.venv\Scripts\ruff.exe check .
```

---

## 4. Decisiones Pendientes (DEC-017)
- **Persistencia de Asistencia:** La persistencia oficial de asistencias no está resuelta (Escenario A: delegado en el Módulo Central vs. Escenario B: persistencia local con sincronización). El puerto `IAttendanceGateway` en `apps/core/domain/ports.py` aísla al sistema para soportar cualquiera de las dos alternativas institucionales sin refactorizar el dominio.
