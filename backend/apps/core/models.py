"""
Modelos de dominio del Módulo Profesor — Sistema de Gestión Académica (SGA).

Basado en la especificación formal SPEC-002 v1.1.
Separa claramente:
1. Referencias académicas maestras (consumidas del SGA central).
2. Conceptos propios del Sistema Profesor (InstanciaClase, ObservacionAcademica).
3. Reglas de asistencia cerradas (EstadoAsistencia) manteniendo desacoplada
   la persistencia oficial según DEC-017.
"""

import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

# ==============================================================================
# Enumeraciones del Dominio
# ==============================================================================


class EstadoAsistencia(models.TextChoices):
    """
    Estados tipados cerrados de asistencia de acuerdo a DEC-004 y R-ASI-01.
    No se admiten estados libres ni valores nulos.
    """

    PRESENTE = "PRESENTE", "Presente"
    AUSENTE = "AUSENTE", "Ausente"
    TARDE = "TARDE", "Tarde"


# ==============================================================================
# Referencias Maestras Académicas (Solo Lectura / Soporte Local)
# ==============================================================================


class PeriodoLectivo(models.Model):
    """
    Intervalo temporal académico oficial que enmarca las cursadas y comisiones.
    Regla R-PER-01 (DEC-007): el período activo se determina por regla, no hardcoded.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=50, unique=True, help_text="Ej: 2026-1C")
    nombre = models.CharField(max_length=100, help_text="Ej: Primer Cuatrimestre 2026")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    es_vigente = models.BooleanField(
        default=False,
        help_text="Indica si es el período académicamente activo por defecto.",
    )

    class Meta:
        verbose_name = "Período Lectivo"
        verbose_name_plural = "Períodos Lectivos"
        ordering = ["-fecha_inicio"]

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

    def clean(self):
        if self.fecha_inicio and self.fecha_fin and self.fecha_inicio > self.fecha_fin:
            raise ValidationError(
                {
                    "fecha_fin": "La fecha de fin no puede ser anterior a la fecha de inicio."
                }
            )

    @classmethod
    def obtener_vigente(cls, fecha=None):
        """
        Resuelve determinísticamente el período lectivo vigente (R-PER-01).
        Si se especifica fecha, busca el período que la contenga; si no,
        el marcado como es_vigente=True o el más reciente.
        """
        if fecha:
            periodo = cls.objects.filter(
                fecha_inicio__lte=fecha, fecha_fin__gte=fecha
            ).first()
            if periodo:
                return periodo
        return cls.objects.filter(es_vigente=True).first()


class Profesor(models.Model):
    """
    Agente pedagógico autenticado. Sujeto de autorización por comisión (R-DOC-01).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    identificador_laboral = models.CharField(
        max_length=50, unique=True, help_text="Legajo o DNI del docente"
    )
    nombre_completo = models.CharField(max_length=150)
    email = models.EmailField(blank=True, default="")
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Profesor"
        verbose_name_plural = "Profesores"
        ordering = ["nombre_completo"]

    def __str__(self):
        return f"{self.nombre_completo} ({self.identificador_laboral})"


class Materia(models.Model):
    """
    Espacio curricular definido en el plan de estudios institucional.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=50, unique=True, help_text="Ej: MAT-101")
    nombre = models.CharField(max_length=150)

    class Meta:
        verbose_name = "Materia"
        verbose_name_plural = "Materias"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} [{self.codigo}]"


class Comision(models.Model):
    """
    Unidad operativa central del dictado de clases (división, turno, año).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=50, help_text="Ej: 1A-NOCHE")
    descripcion = models.CharField(max_length=200, blank=True, default="")
    periodo_lectivo = models.ForeignKey(
        PeriodoLectivo, on_delete=models.PROTECT, related_name="comisiones"
    )
    materias = models.ManyToManyField(Materia, related_name="comisiones", blank=True)

    class Meta:
        verbose_name = "Comisión"
        verbose_name_plural = "Comisiones"
        unique_together = [("codigo", "periodo_lectivo")]
        ordering = ["codigo"]

    def __str__(self):
        return f"Comisión {self.codigo} — {self.periodo_lectivo.codigo}"

    def tiene_docente_asignado(self, profesor, fecha=None):
        """Verifica si un profesor tiene asignación activa en esta comisión."""
        qs = self.asignaciones_docentes.filter(profesor=profesor, activo=True)
        if fecha:
            qs = qs.filter(
                models.Q(fecha_desde__isnull=True) | models.Q(fecha_desde__lte=fecha),
                models.Q(fecha_hasta__isnull=True) | models.Q(fecha_hasta__gte=fecha),
            )
        return qs.exists()


class AsignacionDocente(models.Model):
    """
    Vínculo formal entre un Profesor y una Comisión para un Período Lectivo.
    Base de la autorización en servidor (R-DOC-01, DEC-005).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profesor = models.ForeignKey(
        Profesor, on_delete=models.PROTECT, related_name="asignaciones"
    )
    comision = models.ForeignKey(
        Comision, on_delete=models.PROTECT, related_name="asignaciones_docentes"
    )
    rol_docente = models.CharField(
        max_length=50, default="TITULAR", help_text="Ej: TITULAR, ADJUNTO, SUPLENTE"
    )
    activo = models.BooleanField(default=True)
    fecha_desde = models.DateField(null=True, blank=True)
    fecha_hasta = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Asignación Docente"
        verbose_name_plural = "Asignaciones Docentes"
        unique_together = [("profesor", "comision", "rol_docente")]

    def __str__(self):
        return f"{self.profesor} en {self.comision} ({self.rol_docente})"

    def clean(self):
        if (
            self.fecha_desde
            and self.fecha_hasta
            and self.fecha_desde > self.fecha_hasta
        ):
            raise ValidationError(
                {"fecha_hasta": "La fecha hasta no puede ser previa a la fecha desde."}
            )

    def esta_activa(self, fecha=None):
        """Indica si la asignación está vigente en la fecha provista."""
        if not self.activo:
            return False
        if fecha:
            if self.fecha_desde and fecha < self.fecha_desde:
                return False
            if self.fecha_hasta and fecha > self.fecha_hasta:
                return False
        return True


class Alumno(models.Model):
    """
    Estudiante matriculado en la institución.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    identificador_academico = models.CharField(
        max_length=50, unique=True, help_text="Legajo o DNI del estudiante"
    )
    nombre_completo = models.CharField(max_length=150)
    email = models.EmailField(blank=True, default="")

    class Meta:
        verbose_name = "Alumno"
        verbose_name_plural = "Alumnos"
        ordering = ["nombre_completo"]

    def __str__(self):
        return f"{self.nombre_completo} ({self.identificador_academico})"


class VinculoAlumnoComision(models.Model):
    """
    Inscripción temporal de un alumno en una comisión (SPEC-002, Sección 3 y 4.2).
    Captura altas, bajas o traslados de comisión preservando el historial.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alumno = models.ForeignKey(
        Alumno, on_delete=models.PROTECT, related_name="vinculos_comision"
    )
    comision = models.ForeignKey(
        Comision, on_delete=models.PROTECT, related_name="vinculos_alumnos"
    )
    fecha_inscripcion = models.DateField(default=timezone.now)
    fecha_baja = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha de egreso o cambio de comisión si aplica",
    )
    activo = models.BooleanField(
        default=True,
        help_text="Indica si el estudiante cursa actualmente en la comisión",
    )

    class Meta:
        verbose_name = "Vínculo Alumno-Comisión"
        verbose_name_plural = "Vínculos Alumno-Comisión"
        unique_together = [("alumno", "comision", "fecha_inscripcion")]
        ordering = ["alumno__nombre_completo"]

    def __str__(self):
        estado = "Activo" if self.activo and not self.fecha_baja else "Baja"
        return f"{self.alumno} en {self.comision} [{estado}]"

    def clean(self):
        if (
            self.fecha_inscripcion
            and self.fecha_baja
            and self.fecha_baja < self.fecha_inscripcion
        ):
            raise ValidationError(
                {
                    "fecha_baja": "La fecha de baja no puede ser anterior a la de inscripción."
                }
            )

    def esta_activo_en(self, fecha):
        """Verifica si el alumno pertenecía activamente a la comisión en una fecha."""
        if fecha < self.fecha_inscripcion:
            return False
        if self.fecha_baja and fecha > self.fecha_baja:
            return False
        return True


# ==============================================================================
# Conceptos Propios del Sistema Profesor (Custodiados Nativamente)
# ==============================================================================


class InstanciaClase(models.Model):
    """
    Sesión pedagógica concreta para una comisión (SPEC-002, R-CLS-01).
    Tiene identidad propia e independiente (UUID opaco): una comisión puede
    tener múltiples clases en una misma fecha (bloque mañana / bloque tarde).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comision = models.ForeignKey(
        Comision, on_delete=models.PROTECT, related_name="instancias_clase"
    )
    docente_registrador = models.ForeignKey(
        Profesor, on_delete=models.PROTECT, related_name="clases_registradas"
    )
    fecha = models.DateField(help_text="Fecha de calendario de la clase")
    descripcion_opcional = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Ej: Bloque Teórico Mañana, Taller Práctico Tarde",
    )
    fecha_hora_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Instancia de Clase"
        verbose_name_plural = "Instancias de Clase"
        ordering = ["-fecha", "-fecha_hora_registro"]

    def __str__(self):
        desc = f" ({self.descripcion_opcional})" if self.descripcion_opcional else ""
        return f"Clase {self.fecha} — {self.comision.codigo}{desc}"

    def clean(self):
        # R-CLS-02 / R-DOC-01: El docente registrador debe tener asignación en la comisión
        if self.comision_id and self.docente_registrador_id:
            if not self.comision.tiene_docente_asignado(
                self.docente_registrador, fecha=self.fecha
            ):
                raise ValidationError(
                    {
                        "docente_registrador": (
                            "El docente no posee asignación activa en esta comisión "
                            "para la fecha especificada."
                        )
                    }
                )


class ObservacionAcademica(models.Model):
    """
    Registro cualitativo de seguimiento pedagógico (SPEC-002, 5.4).
    Registra doble marca de tiempo (R-OBS-04):
    - fecha_hecho_pedagogico: fecha del evento observado.
    - fecha_hora_creacion: marca de tiempo del sistema inalterable.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alumno = models.ForeignKey(
        Alumno, on_delete=models.PROTECT, related_name="observaciones_recibidas"
    )
    comision = models.ForeignKey(
        Comision, on_delete=models.PROTECT, related_name="observaciones"
    )
    autor = models.ForeignKey(
        Profesor, on_delete=models.PROTECT, related_name="observaciones_creadas"
    )
    fecha_hecho_pedagogico = models.DateField(
        help_text="Fecha en que ocurrió el hecho pedagógico observado"
    )
    contenido = models.TextField(help_text="Comentario o seguimiento cualitativo")
    fecha_hora_creacion = models.DateTimeField(
        auto_now_add=True, help_text="Marca de tiempo inalterable de auditoría"
    )

    class Meta:
        verbose_name = "Observación Académica"
        verbose_name_plural = "Observaciones Académicas"
        ordering = ["-fecha_hecho_pedagogico", "-fecha_hora_creacion"]

    def __str__(self):
        return (
            f"Obs a {self.alumno.nombre_completo} ({self.fecha_hecho_pedagogico}) "
            f"por {self.autor.nombre_completo}"
        )

    def clean(self):
        # R-OBS-03: Contenido no vacío
        if not self.contenido or not self.contenido.strip():
            raise ValidationError(
                {"contenido": "El contenido de la observación no puede estar vacío."}
            )

        # R-OBS-02: El alumno debe pertenecer o haber pertenecido a la comisión
        if self.alumno_id and self.comision_id:
            vinculo = VinculoAlumnoComision.objects.filter(
                alumno_id=self.alumno_id, comision_id=self.comision_id
            ).first()
            if not vinculo:
                raise ValidationError(
                    {
                        "alumno": "El estudiante no posee ningún vínculo de inscripción con esta comisión."
                    }
                )
            if self.fecha_hecho_pedagogico and not vinculo.esta_activo_en(
                self.fecha_hecho_pedagogico
            ):
                raise ValidationError(
                    {
                        "fecha_hecho_pedagogico": (
                            "La fecha del hecho pedagógico no coincide con el período de "
                            "inscripción del alumno en la comisión."
                        )
                    }
                )

        # R-DOC-01: El autor debe tener asignación en la comisión
        if self.autor_id and self.comision_id:
            if not self.comision.tiene_docente_asignado(self.autor):
                raise ValidationError(
                    {
                        "autor": "El docente autor no tiene asignación registrada en esta comisión."
                    }
                )
