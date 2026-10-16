"""
Serializadores REST para el Módulo Profesor.
"""

from rest_framework import serializers

from apps.core.models import (
    Alumno,
    Comision,
    InstanciaClase,
    Materia,
    ObservacionAcademica,
    PeriodoLectivo,
    Profesor,
    VinculoAlumnoComision,
)


class ProfesorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profesor
        fields = ["id", "identificador_laboral", "nombre_completo", "email", "activo"]


class ItemAsistenciaInputSerializer(serializers.Serializer):
    alumno_id = serializers.UUIDField()
    estado = serializers.ChoiceField(choices=["PRESENTE", "AUSENTE", "TARDE"])


class MateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = ["id", "codigo", "nombre"]


class PeriodoLectivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodoLectivo
        fields = ["id", "codigo", "nombre", "fecha_inicio", "fecha_fin", "es_vigente"]


class ComisionDocenteSerializer(serializers.ModelSerializer):
    """Serializador de comisiones para la vista del docente."""

    periodo_lectivo = PeriodoLectivoSerializer(read_only=True)
    materias = MateriaSerializer(many=True, read_only=True)

    class Meta:
        model = Comision
        fields = [
            "id",
            "codigo",
            "descripcion",
            "periodo_lectivo",
            "materias",
        ]


class AlumnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alumno
        fields = ["id", "identificador_academico", "nombre_completo", "email"]


class NominaAlumnoSerializer(serializers.ModelSerializer):
    """Representación del alumno en el contexto de una comisión (con dimensión temporal)."""

    alumno = AlumnoSerializer(read_only=True)

    class Meta:
        model = VinculoAlumnoComision
        fields = [
            "id",
            "alumno",
            "fecha_inscripcion",
            "fecha_baja",
            "activo",
        ]


class InstanciaClaseSerializer(serializers.ModelSerializer):
    """Serializador para instancias de clase (sesiones pedagógicas concretas)."""

    class Meta:
        model = InstanciaClase
        fields = [
            "id",
            "comision",
            "docente_registrador",
            "fecha",
            "descripcion_opcional",
            "fecha_hora_registro",
        ]
        read_only_fields = ["id", "fecha_hora_registro"]

    def validate(self, attrs):
        instancia = InstanciaClase(**attrs)
        instancia.clean()
        return attrs


class ObservacionAcademicaSerializer(serializers.ModelSerializer):
    """Serializador para lectura y creación de observaciones pedagógicas."""

    autor_nombre = serializers.CharField(source="autor.nombre_completo", read_only=True)
    alumno_nombre = serializers.CharField(
        source="alumno.nombre_completo", read_only=True
    )

    class Meta:
        model = ObservacionAcademica
        fields = [
            "id",
            "comision",
            "alumno",
            "alumno_nombre",
            "autor",
            "autor_nombre",
            "fecha_hecho_pedagogico",
            "contenido",
            "fecha_hora_creacion",
        ]
        read_only_fields = [
            "id",
            "fecha_hora_creacion",
            "autor_nombre",
            "alumno_nombre",
        ]

    def validate(self, attrs):
        observacion = ObservacionAcademica(**attrs)
        observacion.clean()
        return attrs
