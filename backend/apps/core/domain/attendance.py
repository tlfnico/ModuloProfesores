"""
Lógica y reglas de negocio del dominio de Asistencia.

Respeta estrictamente DEC-004, DEC-017 y las reglas R-ASI-01, R-ASI-02 y R-ASI-03:
- Estados permitidos únicamente: PRESENTE, AUSENTE, TARDE.
- Tomas parciales admitidas: alumnos sin estado no son equivalentes a AUSENTE.
- Idempotencia: el reenvío idéntico no duplica registros.
- Desacoplado de la persistencia oficial según la cuestión institucional DEC-017.
"""

from dataclasses import dataclass
from typing import Dict, List, Set

from apps.core.models import EstadoAsistencia, InstanciaClase, VinculoAlumnoComision


class AttendanceDomainError(Exception):
    """Error en las reglas de negocio de asistencia."""

    pass


@dataclass(frozen=True)
class AttendanceItem:
    """Representación inmutable de una marca de asistencia en el dominio."""

    alumno_id: str
    estado: str

    def __post_init__(self):
        estados_validos = {e.value for e in EstadoAsistencia}
        if self.estado not in estados_validos:
            raise AttendanceDomainError(
                f"Estado '{self.estado}' inválido. Los únicos estados permitidos "
                f"son: {', '.join(sorted(estados_validos))}."
            )


class AttendanceService:
    """
    Servicio de dominio para validación y procesamiento de toma de asistencia.
    """

    @staticmethod
    def validar_lote_asistencia(
        instancia_clase: InstanciaClase,
        registros: List[AttendanceItem],
    ) -> Dict[str, str]:
        """
        Valida que un lote de asistencia cumpla con las reglas del dominio:
        1. Estados cerrados y válidos.
        2. Alumnos activos o vinculados a la comisión de la clase en la fecha.
        3. No duplicados dentro del mismo lote.
        4. Tomas parciales admitidas (R-ASI-02): no se exige que estén todos los alumnos.

        Retorna un diccionario mapeando alumno_id -> estado validado.
        """
        if not registros:
            raise AttendanceDomainError("El lote de asistencia no puede estar vacío.")

        # Obtener alumnos con inscripción válida en la comisión para la fecha de la clase
        vinculos_activos = VinculoAlumnoComision.objects.filter(
            comision=instancia_clase.comision
        )
        alumnos_habilitados_ids: Set[str] = {
            str(v.alumno_id)
            for v in vinculos_activos
            if v.esta_activo_en(instancia_clase.fecha)
        }

        alumnos_en_lote: Set[str] = set()
        resultado: Dict[str, str] = {}

        for item in registros:
            alumno_str = str(item.alumno_id)

            if alumno_str in alumnos_en_lote:
                raise AttendanceDomainError(
                    f"El alumno {alumno_str} aparece duplicado en el lote de asistencia."
                )

            if alumno_str not in alumnos_habilitados_ids:
                raise AttendanceDomainError(
                    f"El alumno {alumno_str} no pertenece activamente a la "
                    f"comisión {instancia_clase.comision.codigo} en la fecha {instancia_clase.fecha}."
                )

            alumnos_en_lote.add(alumno_str)
            resultado[alumno_str] = item.estado

        # R-ASI-02: La toma parcial es válida. No forzamos que alumnos_en_lote cubra a todos.
        return resultado
