"""
Controladores de API REST para el Módulo Profesor.

Aplica estrictamente las directrices Zero Trust y Scope Docente (R-DOC-01):
el profesor solo puede operar sobre sus comisiones asignadas en el período activo.
"""

from uuid import UUID

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.api.serializers import (
    ComisionDocenteSerializer,
    InstanciaClaseSerializer,
    ItemAsistenciaInputSerializer,
    NominaAlumnoSerializer,
    ObservacionAcademicaSerializer,
    ProfesorSerializer,
)
from apps.core.models import (
    Comision,
    InstanciaClase,
    ObservacionAcademica,
    PeriodoLectivo,
    Profesor,
    VinculoAlumnoComision,
)


def obtener_docente_autenticado(request) -> Profesor:
    """
    Resuelve la identidad docente desde la cabecera X-Profesor-Id o parámetro.
    Aísla al backend del protocolo institucional definitivo según DEC-016 y DEC-028.
    """
    profesor_id = request.headers.get("X-Profesor-Id") or request.query_params.get(
        "profesor_id"
    )
    if not profesor_id:
        raise PermissionDenied(
            "Debe identificarse un docente mediante la cabecera 'X-Profesor-Id'."
        )

    try:
        if isinstance(profesor_id, str):
            profesor_uuid = UUID(profesor_id)
            profesor = Profesor.objects.filter(id=profesor_uuid, activo=True).first()
        else:
            profesor = None
    except ValueError:
        # Intento de búsqueda por identificador_laboral (legajo o DNI)
        profesor = Profesor.objects.filter(
            identificador_laboral=profesor_id, activo=True
        ).first()

    if not profesor:
        raise PermissionDenied("Docente no encontrado o no activo en el sistema.")

    return profesor


class ComisionesDocenteView(APIView):
    """
    F1 — Consulta de comisiones asignadas al docente autenticado en el período activo.
    """

    @extend_schema(
        summary="Listar comisiones asignadas",
        description="Retorna las comisiones en las que el docente tiene asignación activa para el período lectivo vigente (R-DOC-01).",
        parameters=[
            OpenApiParameter(
                name="X-Profesor-Id",
                type=str,
                location=OpenApiParameter.HEADER,
                description="Identificador UUID o legajo del docente autenticado.",
                required=True,
            ),
            OpenApiParameter(
                name="periodo_id",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filtrar por período lectivo específico (opcional; por defecto el vigente).",
                required=False,
            ),
        ],
        responses={200: ComisionDocenteSerializer(many=True)},
    )
    def get(self, request):
        docente = obtener_docente_autenticado(request)
        periodo_id = request.query_params.get("periodo_id")

        if periodo_id:
            try:
                UUID(str(periodo_id))
                periodo = get_object_or_404(PeriodoLectivo, id=periodo_id)
            except ValueError:
                periodo = PeriodoLectivo.objects.filter(codigo=periodo_id).first()
                if not periodo:
                    return Response(
                        {"detail": f"Período lectivo '{periodo_id}' no encontrado."},
                        status=status.HTTP_404_NOT_FOUND,
                    )
        else:
            periodo = PeriodoLectivo.obtener_vigente()

        if not periodo:
            return Response(
                {
                    "mensaje": "No se determinó un período lectivo activo.",
                    "comisiones": [],
                },
                status=status.HTTP_200_OK,
            )

        # R-DOC-01: Filtrar estrictamente comisiones con asignación activa para el docente
        comisiones = Comision.objects.filter(
            periodo_lectivo=periodo,
            asignaciones_docentes__profesor=docente,
            asignaciones_docentes__activo=True,
        ).distinct()

        serializer = ComisionDocenteSerializer(comisiones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NominaComisionView(APIView):
    """
    F2 — Consulta de nómina de alumnos matriculados en una comisión asignada.
    """

    @extend_schema(
        summary="Consultar nómina de alumnos",
        description="Retorna los estudiantes matriculados en la comisión especificada con control estricto de scope docente (Zero Trust).",
        parameters=[
            OpenApiParameter(
                name="X-Profesor-Id",
                type=str,
                location=OpenApiParameter.HEADER,
                description="Identificador UUID o legajo del docente autenticado.",
                required=True,
            ),
            OpenApiParameter(
                name="incluir_bajas",
                type=bool,
                location=OpenApiParameter.QUERY,
                description="Incluir estudiantes que fueron dados de baja de la comisión.",
                required=False,
            ),
        ],
        responses={
            200: NominaAlumnoSerializer(many=True),
            403: OpenApiResponse(
                description="El docente no tiene asignada esta comisión."
            ),
        },
    )
    def get(self, request, comision_id):
        docente = obtener_docente_autenticado(request)
        comision = get_object_or_404(Comision, id=comision_id)

        # R-DOC-01: Verificación de Scope Docente en el Servidor
        if not comision.tiene_docente_asignado(docente):
            raise PermissionDenied(
                "Acceso denegado: el docente no tiene asignada esta comisión."
            )

        incluir_bajas = (
            request.query_params.get("incluir_bajas", "false").lower() == "true"
        )
        vinculos = VinculoAlumnoComision.objects.filter(comision=comision)
        if not incluir_bajas:
            vinculos = vinculos.filter(activo=True)

        serializer = NominaAlumnoSerializer(vinculos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InstanciaClaseListCreateView(APIView):
    """
    Gestión de sesiones pedagógicas (Instancias de Clase) de una comisión.
    """

    @extend_schema(
        summary="Listar instancias de clase de la comisión",
        description="Lista las sesiones de clase registradas para la comisión.",
        parameters=[
            OpenApiParameter(
                name="X-Profesor-Id",
                type=str,
                location=OpenApiParameter.HEADER,
                required=True,
            ),
        ],
        responses={200: InstanciaClaseSerializer(many=True)},
    )
    def get(self, request, comision_id):
        docente = obtener_docente_autenticado(request)
        comision = get_object_or_404(Comision, id=comision_id)

        if not comision.tiene_docente_asignado(docente):
            raise PermissionDenied(
                "Acceso denegado: el docente no tiene asignada esta comisión."
            )

        clases = InstanciaClase.objects.filter(comision=comision).order_by("-fecha")
        serializer = InstanciaClaseSerializer(clases, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Crear nueva instancia de clase",
        description="Registra una nueva sesión pedagógica. Admite múltiples clases en la misma fecha (R-CLS-01).",
        request=InstanciaClaseSerializer,
        responses={201: InstanciaClaseSerializer},
    )
    def post(self, request, comision_id):
        docente = obtener_docente_autenticado(request)
        comision = get_object_or_404(Comision, id=comision_id)

        if not comision.tiene_docente_asignado(docente):
            raise PermissionDenied(
                "Acceso denegado: el docente no tiene asignada esta comisión."
            )

        if not isinstance(request.data, dict):
            return Response(
                {"detail": "Se esperaba un objeto JSON válido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = request.data.copy()
        data["comision"] = str(comision.id)
        data["docente_registrador"] = str(docente.id)

        serializer = InstanciaClaseSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObservacionListCreateView(APIView):
    """
    F5 — Consulta y registro de observaciones académicas por alumno y comisión.
    """

    @extend_schema(
        summary="Listar observaciones de la comisión",
        description="Retorna las observaciones pedagógicas registradas en la comisión.",
        parameters=[
            OpenApiParameter(
                name="X-Profesor-Id",
                type=str,
                location=OpenApiParameter.HEADER,
                required=True,
            ),
            OpenApiParameter(
                name="alumno_id",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filtrar observaciones de un alumno específico (opcional).",
                required=False,
            ),
        ],
        responses={200: ObservacionAcademicaSerializer(many=True)},
    )
    def get(self, request, comision_id):
        docente = obtener_docente_autenticado(request)
        comision = get_object_or_404(Comision, id=comision_id)

        if not comision.tiene_docente_asignado(docente):
            raise PermissionDenied(
                "Acceso denegado: el docente no tiene asignada esta comisión."
            )

        qs = ObservacionAcademica.objects.filter(comision=comision)
        alumno_id = request.query_params.get("alumno_id")
        if alumno_id:
            try:
                UUID(str(alumno_id))
                qs = qs.filter(alumno_id=alumno_id)
            except ValueError:
                # Soporta búsqueda por legajo/DNI alternativo
                qs = qs.filter(alumno__identificador_academico=alumno_id)

        serializer = ObservacionAcademicaSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Registrar observación académica",
        description="Crea una observación con doble marca de tiempo (hecho pedagógico vs creación, R-OBS-04).",
        request=ObservacionAcademicaSerializer,
        responses={201: ObservacionAcademicaSerializer},
    )
    def post(self, request, comision_id):
        docente = obtener_docente_autenticado(request)
        comision = get_object_or_404(Comision, id=comision_id)

        if not comision.tiene_docente_asignado(docente):
            raise PermissionDenied(
                "Acceso denegado: el docente no tiene asignada esta comisión."
            )

        if not isinstance(request.data, dict):
            return Response(
                {"detail": "Se esperaba un objeto JSON válido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = request.data.copy()
        data["comision"] = str(comision.id)
        data["autor"] = str(docente.id)

        serializer = ObservacionAcademicaSerializer(data=data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as exc:
                raise ValidationError(str(exc))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListaProfesoresView(APIView):
    """
    Permite listar los docentes activos en el sistema para seleccionar
    el perfil en entorno de desarrollo.
    """

    @extend_schema(
        summary="Listar profesores disponibles (modo desarrollo)",
        description="Devuelve el catálogo de docentes para seleccionar el identificador X-Profesor-Id en desarrollo.",
        responses={200: ProfesorSerializer(many=True)},
    )
    def get(self, request):
        profesores = Profesor.objects.filter(activo=True)
        serializer = ProfesorSerializer(profesores, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PerfilProfesorView(APIView):
    """
    Devuelve los datos de identidad del docente identificado mediante X-Profesor-Id.
    """

    @extend_schema(
        summary="Consultar perfil del docente autenticado",
        description="Retorna la identidad básica del docente actual.",
        responses={200: ProfesorSerializer},
    )
    def get(self, request):
        docente = obtener_docente_autenticado(request)
        serializer = ProfesorSerializer(docente)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ValidarLoteAsistenciaView(APIView):
    """
    Valida un lote de asistencia áulica en el servidor según las reglas de dominio
    (SPEC-002, R-ASI-01 a R-ASI-03), reportando estado de persistencia según DEC-017.
    """

    @extend_schema(
        summary="Validar y procesar lote de asistencia áulica",
        description=(
            "Valida la lista de alumnos y estados contra la nómina de la comisión. "
            "Aplica R-ASI-02 (tomas parciales válidas) y reporta el estado de persistencia institucional (DEC-017)."
        ),
        parameters=[
            OpenApiParameter(
                name="X-Profesor-Id",
                type=str,
                location=OpenApiParameter.HEADER,
                required=True,
            ),
        ],
        request=ItemAsistenciaInputSerializer(many=True),
        responses={200: OpenApiResponse(description="Lote validado exitosamente")},
    )
    def post(self, request, comision_id, clase_id):
        docente = obtener_docente_autenticado(request)
        comision = get_object_or_404(Comision, id=comision_id)
        clase = get_object_or_404(InstanciaClase, id=clase_id, comision=comision)

        if not comision.tiene_docente_asignado(docente):
            raise PermissionDenied(
                "Acceso denegado: el docente no tiene asignada esta comisión."
            )

        registros_data = request.data
        if not isinstance(registros_data, list):
            return Response(
                {"detail": "Se esperaba una lista de marcas de asistencia."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ItemAsistenciaInputSerializer(data=registros_data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Convertir a objetos del dominio
        from apps.core.domain.attendance import (
            AttendanceDomainError,
            AttendanceItem,
            AttendanceService,
        )

        items_dominio = [
            AttendanceItem(alumno_id=str(item["alumno_id"]), estado=item["estado"])
            for item in serializer.validated_data
        ]

        try:
            validados = AttendanceService.validar_lote_asistencia(clase, items_dominio)
        except AttendanceDomainError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        # Calcular métricas del lote
        total_nomina = VinculoAlumnoComision.objects.filter(
            comision=comision, activo=True
        ).count()
        presentes = sum(1 for e in validados.values() if e == "PRESENTE")
        ausentes = sum(1 for e in validados.values() if e == "AUSENTE")
        tardes = sum(1 for e in validados.values() if e == "TARDE")
        marcados = len(validados)
        sin_marcar = max(0, total_nomina - marcados)

        return Response(
            {
                "valido": True,
                "comision_codigo": comision.codigo,
                "instancia_clase_id": str(clase.id),
                "fecha_clase": str(clase.fecha),
                "resumen": {
                    "total_nomina": total_nomina,
                    "marcados": marcados,
                    "presentes": presentes,
                    "ausentes": ausentes,
                    "tardes": tardes,
                    "sin_marcar": sin_marcar,
                },
                "es_toma_parcial": sin_marcar > 0,
                "estado_persistencia": "PENDIENTE_RESOLUCION_INSTITUCIONAL (DEC-017)",
                "mensaje": (
                    "Lote de asistencia validado correctamente según las reglas de dominio. "
                    "Nota técnica: La persistencia definitiva de asistencia continúa en evaluación "
                    "institucional según DEC-017 (Escenario A: Módulo Central vs. Escenario B: Local)."
                ),
                "registros_validados": validados,
            },
            status=status.HTTP_200_OK,
        )
