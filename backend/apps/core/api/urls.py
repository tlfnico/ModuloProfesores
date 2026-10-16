"""
Rutas de la API REST del Módulo Profesor.
"""

from django.urls import path

from apps.core.api.views import (
    ComisionesDocenteView,
    InstanciaClaseListCreateView,
    ListaProfesoresView,
    NominaComisionView,
    ObservacionListCreateView,
    PerfilProfesorView,
    ValidarLoteAsistenciaView,
)

urlpatterns = [
    # Catálogo de profesores (para selección en modo desarrollo)
    path("profesores/", ListaProfesoresView.as_view(), name="profesores-list"),
    # Perfil del docente autenticado
    path("profesor/perfil/", PerfilProfesorView.as_view(), name="profesor-perfil"),
    # F1 — Comisiones asignadas al docente
    path(
        "profesor/comisiones/",
        ComisionesDocenteView.as_view(),
        name="profesor-comisiones",
    ),
    # F2 — Nómina de estudiantes por comisión
    path(
        "comisiones/<uuid:comision_id>/alumnos/",
        NominaComisionView.as_view(),
        name="comision-alumnos",
    ),
    # Instancias de clase por comisión
    path(
        "comisiones/<uuid:comision_id>/clases/",
        InstanciaClaseListCreateView.as_view(),
        name="comision-clases",
    ),
    # F4 / F3 — Validación y procesamiento áulico de asistencia (DEC-017)
    path(
        "comisiones/<uuid:comision_id>/clases/<uuid:clase_id>/asistencia/validar/",
        ValidarLoteAsistenciaView.as_view(),
        name="clase-asistencia-validar",
    ),
    # F5 — Observaciones académicas por comisión
    path(
        "comisiones/<uuid:comision_id>/observaciones/",
        ObservacionListCreateView.as_view(),
        name="comision-observaciones",
    ),
]
