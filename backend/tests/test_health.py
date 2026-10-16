"""
Pruebas iniciales de verificación de arranque del backend.

Estas pruebas comprueban que:
- El servidor Django responde correctamente.
- El endpoint de salud devuelve el formato esperado.
- La documentación OpenAPI se genera sin errores.
"""

from django.test import Client


class TestHealthCheck:
    """Pruebas del endpoint de verificación de salud."""

    def test_health_check_returns_200(self, client: Client):
        """El endpoint /api/health/ responde con HTTP 200."""
        response = client.get("/api/health/")
        assert response.status_code == 200

    def test_health_check_response_body(self, client: Client):
        """El cuerpo de la respuesta contiene status y nombre del servicio."""
        response = client.get("/api/health/")
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "sistema-profesor-backend"


class TestOpenAPISchema:
    """Pruebas de generación de esquema OpenAPI."""

    def test_schema_endpoint_returns_200(self, client: Client):
        """El endpoint /api/schema/ genera el esquema sin errores."""
        response = client.get("/api/schema/")
        assert response.status_code == 200

    def test_swagger_ui_returns_200(self, client: Client):
        """La interfaz Swagger UI se sirve correctamente."""
        response = client.get("/api/docs/")
        assert response.status_code == 200
