"""
URL configuration for config project — Sistema Profesor (SGA).

Rutas raíz del backend. Cada app del dominio registrará sus propias rutas
mediante include() cuando se implemente.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.utils import OpenApiResponse, extend_schema
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response


@extend_schema(
    summary="Verificación de salud",
    description="Devuelve el estado de disponibilidad del backend del Módulo Profesor.",
    responses={
        200: OpenApiResponse(
            description="El servicio se encuentra operativo.",
        )
    },
)
@api_view(["GET"])
def health_check(request):
    """Endpoint de verificación de salud del backend."""
    return Response({"status": "ok", "service": "sistema-profesor-backend"})


urlpatterns = [
    path("admin/", admin.site.urls),
    # Health check
    path("api/health/", health_check, name="health-check"),
    # API del Módulo Profesor
    path("api/", include("apps.core.api.urls")),
    # Documentación OpenAPI (solo desarrollo)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
