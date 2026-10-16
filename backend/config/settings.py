"""
Django settings for config project — Sistema Profesor (SGA).

Configuración de desarrollo local.
Los valores sensibles se leen desde variables de entorno mediante python-decouple.
Ver .env.example para la lista completa de variables requeridas.
"""

from pathlib import Path

from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Seguridad
# ---------------------------------------------------------------------------

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-dev-only-change-in-production",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1",
    cast=lambda v: [h.strip() for h in v.split(",")],
)


# ---------------------------------------------------------------------------
# Aplicaciones instaladas
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Terceros
    "rest_framework",
    "drf_spectacular",
    # Módulos del Sistema Profesor
    "apps.core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# ---------------------------------------------------------------------------
# Base de datos — PostgreSQL
# ---------------------------------------------------------------------------
# La conexión se configura mediante variables de entorno.
# En desarrollo local, los valores por defecto apuntan a PostgreSQL local.

DB_ENGINE = config("DB_ENGINE", default="django.db.backends.postgresql")

if DB_ENGINE == "django.db.backends.sqlite3":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": config("DB_NAME", default="sga_profesor"),
            "USER": config("DB_USER", default="postgres"),
            "PASSWORD": config("DB_PASSWORD", default="postgres"),
            "HOST": config("DB_HOST", default="localhost"),
            "PORT": config("DB_PORT", default="5432"),
        }
    }


# ---------------------------------------------------------------------------
# Validadores de contraseña
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ---------------------------------------------------------------------------
# Internacionalización
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "es-ar"

TIME_ZONE = "America/Argentina/Buenos_Aires"

USE_I18N = True

USE_TZ = True


# ---------------------------------------------------------------------------
# Archivos estáticos
# ---------------------------------------------------------------------------

STATIC_URL = "static/"


# ---------------------------------------------------------------------------
# Clave primaria por defecto
# ---------------------------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
}

# Si estamos en desarrollo, agregamos el BrowsableAPIRenderer para facilitar
# la exploración de la API en el navegador.
if DEBUG:
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"].append(
        "rest_framework.renderers.BrowsableAPIRenderer"
    )


# ---------------------------------------------------------------------------
# drf-spectacular — Documentación OpenAPI
# ---------------------------------------------------------------------------

SPECTACULAR_SETTINGS = {
    "TITLE": "Sistema Profesor — API",
    "DESCRIPTION": (
        "API REST del Módulo Profesor del Sistema de Gestión Académica. "
        "Los contratos definitivos se definirán una vez aprobados los "
        "diseños de dominio y las especificaciones de integración."
    ),
    "VERSION": "0.1.0-dev",
    "SERVE_INCLUDE_SCHEMA": False,
}
