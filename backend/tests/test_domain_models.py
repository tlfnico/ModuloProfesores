"""
Pruebas automatizadas de modelos de dominio y reglas de negocio del Módulo Profesor.
Valida SPEC-002 v1.1.
"""

from datetime import date

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.core.domain.attendance import (
    AttendanceDomainError,
    AttendanceItem,
    AttendanceService,
)
from apps.core.models import (
    Alumno,
    AsignacionDocente,
    Comision,
    EstadoAsistencia,
    InstanciaClase,
    ObservacionAcademica,
    PeriodoLectivo,
    Profesor,
    VinculoAlumnoComision,
)


@pytest.mark.django_db
class TestPeriodoLectivo:
    """Pruebas del modelo Período Lectivo y resolución dinámica (R-PER-01)."""

    def test_valida_fechas_coherentes(self):
        """La fecha de fin no puede ser anterior a la fecha de inicio."""
        periodo = PeriodoLectivo(
            codigo="2026-INV",
            nombre="Invalido",
            fecha_inicio=date(2026, 6, 1),
            fecha_fin=date(2026, 5, 1),
        )
        with pytest.raises(ValidationError):
            periodo.clean()

    def test_obtener_vigente_por_defecto(self):
        """Retorna el período marcado como es_vigente=True."""
        PeriodoLectivo.objects.create(
            codigo="2025-2C",
            nombre="2do Cuatrimestre 2025",
            fecha_inicio=date(2025, 8, 1),
            fecha_fin=date(2025, 12, 15),
            es_vigente=False,
        )
        p2 = PeriodoLectivo.objects.create(
            codigo="2026-1C",
            nombre="1er Cuatrimestre 2026",
            fecha_inicio=date(2026, 3, 1),
            fecha_fin=date(2026, 7, 15),
            es_vigente=True,
        )
        assert PeriodoLectivo.obtener_vigente() == p2

    def test_obtener_vigente_por_fecha(self):
        """Determina determinísticamente el período lectivo según la fecha provista."""
        PeriodoLectivo.objects.create(
            codigo="2026-1C",
            nombre="1er Cuatrimestre 2026",
            fecha_inicio=date(2026, 3, 1),
            fecha_fin=date(2026, 7, 15),
            es_vigente=False,
        )
        p_futuro = PeriodoLectivo.objects.create(
            codigo="2026-2C",
            nombre="2do Cuatrimestre 2026",
            fecha_inicio=date(2026, 8, 1),
            fecha_fin=date(2026, 12, 15),
            es_vigente=False,
        )
        vigente = PeriodoLectivo.obtener_vigente(fecha=date(2026, 9, 10))
        assert vigente == p_futuro


@pytest.mark.django_db
class TestScopeDocente:
    """Pruebas de Scope Docente y Asignaciones (R-DOC-01, DEC-005)."""

    def test_profesor_autorizado_solo_en_sus_comisiones(self):
        """Un profesor solo tiene acceso en comisiones donde tiene asignación activa."""
        periodo = PeriodoLectivo.objects.create(
            codigo="2026-1C",
            nombre="1er Cuatrimestre 2026",
            fecha_inicio=date(2026, 3, 1),
            fecha_fin=date(2026, 7, 15),
            es_vigente=True,
        )
        comision_a = Comision.objects.create(codigo="1A", periodo_lectivo=periodo)
        comision_b = Comision.objects.create(codigo="1B", periodo_lectivo=periodo)

        profesor = Profesor.objects.create(
            identificador_laboral="DOC-100",
            nombre_completo="Profesor Asignado",
        )

        AsignacionDocente.objects.create(
            profesor=profesor,
            comision=comision_a,
            rol_docente="TITULAR",
            activo=True,
        )

        assert comision_a.tiene_docente_asignado(profesor) is True
        assert comision_b.tiene_docente_asignado(profesor) is False

    def test_cese_de_asignacion_docente(self):
        """Si la asignación está inactiva o fuera de rango, no se considera activa."""
        periodo = PeriodoLectivo.objects.create(
            codigo="2026-1C",
            nombre="1er Cuatrimestre 2026",
            fecha_inicio=date(2026, 3, 1),
            fecha_fin=date(2026, 7, 15),
            es_vigente=True,
        )
        comision = Comision.objects.create(codigo="1A", periodo_lectivo=periodo)
        profesor = Profesor.objects.create(
            identificador_laboral="DOC-200",
            nombre_completo="Docente Suplente",
        )

        # Asignación finalizada
        AsignacionDocente.objects.create(
            profesor=profesor,
            comision=comision,
            rol_docente="SUPLENTE",
            activo=False,
        )
        assert comision.tiene_docente_asignado(profesor) is False


@pytest.mark.django_db
class TestVinculoAlumnoComisionTemporal:
    """Pruebas de la dimensión temporal del alumno en la comisión (Escenario límite 2)."""

    def test_cambio_de_comision_preserva_historial(self):
        """Un alumno dado de baja de una comisión mantiene registro histórico pero no vigencia."""
        periodo = PeriodoLectivo.objects.create(
            codigo="2026-1C",
            nombre="1er Cuatrimestre 2026",
            fecha_inicio=date(2026, 3, 1),
            fecha_fin=date(2026, 7, 15),
        )
        comision_origen = Comision.objects.create(codigo="1A", periodo_lectivo=periodo)
        comision_destino = Comision.objects.create(codigo="1B", periodo_lectivo=periodo)

        alumno = Alumno.objects.create(
            identificador_academico="ALU-001",
            nombre_completo="Estudiante Transferido",
        )

        # Cursó en comisión 1A hasta el 1 de abril
        v_antiguo = VinculoAlumnoComision.objects.create(
            alumno=alumno,
            comision=comision_origen,
            fecha_inscripcion=date(2026, 3, 1),
            fecha_baja=date(2026, 4, 1),
            activo=False,
        )
        # Ingresó a comisión 1B el 2 de abril
        v_nuevo = VinculoAlumnoComision.objects.create(
            alumno=alumno,
            comision=comision_destino,
            fecha_inscripcion=date(2026, 4, 2),
            activo=True,
        )

        # El 15 de marzo estaba activo en comision_origen
        assert v_antiguo.esta_activo_en(date(2026, 3, 15)) is True
        assert v_nuevo.esta_activo_en(date(2026, 3, 15)) is False

        # El 15 de abril está activo en comision_destino
        assert v_antiguo.esta_activo_en(date(2026, 4, 15)) is False
        assert v_nuevo.esta_activo_en(date(2026, 4, 15)) is True


@pytest.mark.django_db
class TestInstanciaClase:
    """Pruebas de Instancias de Clase y múltiples sesiones por día (R-CLS-01, Escenario límite 3)."""

    def test_multiples_clases_mismo_dia_tienen_identidad_propia(self):
        """Una comisión puede tener varias clases en una misma fecha sin colisión de unicidad."""
        periodo = PeriodoLectivo.objects.create(
            codigo="2026-1C",
            nombre="1C 2026",
            fecha_inicio=date(2026, 3, 1),
            fecha_fin=date(2026, 7, 15),
        )
        comision = Comision.objects.create(codigo="1A", periodo_lectivo=periodo)
        profesor = Profesor.objects.create(
            identificador_laboral="DOC-300",
            nombre_completo="Profesor Titular",
        )
        AsignacionDocente.objects.create(
            profesor=profesor, comision=comision, activo=True
        )

        fecha_clase = date(2026, 4, 10)

        # Clase 1: Turno Mañana Teórico
        clase_manana = InstanciaClase.objects.create(
            comision=comision,
            docente_registrador=profesor,
            fecha=fecha_clase,
            descripcion_opcional="Bloque Teórico",
        )
        # Clase 2: Turno Tarde Práctico
        clase_tarde = InstanciaClase.objects.create(
            comision=comision,
            docente_registrador=profesor,
            fecha=fecha_clase,
            descripcion_opcional="Taller Práctico",
        )

        assert clase_manana.id != clase_tarde.id
        assert clase_manana.fecha == clase_tarde.fecha
        assert (
            InstanciaClase.objects.filter(comision=comision, fecha=fecha_clase).count()
            == 2
        )

    def test_docente_no_asignado_no_puede_registrar_clase(self):
        """R-CLS-02: El docente registrador debe tener asignación en la comisión."""
        periodo = PeriodoLectivo.objects.create(
            codigo="2026-1C",
            nombre="1C 2026",
            fecha_inicio=date(2026, 3, 1),
            fecha_fin=date(2026, 7, 15),
        )
        comision = Comision.objects.create(codigo="1A", periodo_lectivo=periodo)
        profesor_ajeno = Profesor.objects.create(
            identificador_laboral="DOC-AJENO",
            nombre_completo="Docente Ajeno",
        )

        clase = InstanciaClase(
            comision=comision,
            docente_registrador=profesor_ajeno,
            fecha=date(2026, 4, 10),
        )
        with pytest.raises(ValidationError):
            clase.clean()


@pytest.mark.django_db
class TestObservacionAcademica:
    """Pruebas de Observaciones Académicas (SPEC-002 5.4, R-OBS-01 a R-OBS-04)."""

    def test_doble_marca_de_tiempo_y_creacion_exitosa(self):
        """Diferencia fechaHechoPedagogico de fechaHoraCreacion (R-OBS-04)."""
        periodo = PeriodoLectivo.objects.create(
            codigo="2026-1C",
            nombre="1C 2026",
            fecha_inicio=date(2026, 3, 1),
            fecha_fin=date(2026, 7, 15),
        )
        comision = Comision.objects.create(codigo="1A", periodo_lectivo=periodo)
        profesor = Profesor.objects.create(
            identificador_laboral="DOC-500",
            nombre_completo="Docente Observador",
        )
        AsignacionDocente.objects.create(
            profesor=profesor, comision=comision, activo=True
        )

        alumno = Alumno.objects.create(
            identificador_academico="ALU-050",
            nombre_completo="Alumno Observado",
        )
        VinculoAlumnoComision.objects.create(
            alumno=alumno,
            comision=comision,
            fecha_inscripcion=date(2026, 3, 1),
            activo=True,
        )

        fecha_hecho = date(2026, 4, 5)
        obs = ObservacionAcademica.objects.create(
            alumno=alumno,
            comision=comision,
            autor=profesor,
            fecha_hecho_pedagogico=fecha_hecho,
            contenido="Demostró gran destreza en la resolución práctica de la consigna.",
        )

        assert obs.fecha_hecho_pedagogico == fecha_hecho
        assert obs.fecha_hora_creacion is not None
        # La fecha de creación es la del momento del sistema, no la del hecho pasado
        assert obs.fecha_hora_creacion.date() == timezone.now().date()

    def test_rechaza_contenido_vacio(self):
        """R-OBS-03: Rechaza contenido vacío o solo espacios en blanco."""
        periodo = PeriodoLectivo.objects.create(
            codigo="2026-1C",
            nombre="1C 2026",
            fecha_inicio=date(2026, 3, 1),
            fecha_fin=date(2026, 7, 15),
        )
        comision = Comision.objects.create(codigo="1A", periodo_lectivo=periodo)
        profesor = Profesor.objects.create(
            identificador_laboral="DOC-501", nombre_completo="Docente"
        )
        AsignacionDocente.objects.create(profesor=profesor, comision=comision)
        alumno = Alumno.objects.create(
            identificador_academico="ALU-051", nombre_completo="Alumno"
        )
        VinculoAlumnoComision.objects.create(
            alumno=alumno, comision=comision, fecha_inscripcion=date(2026, 3, 1)
        )

        obs = ObservacionAcademica(
            alumno=alumno,
            comision=comision,
            autor=profesor,
            fecha_hecho_pedagogico=date(2026, 4, 5),
            contenido="    ",
        )
        with pytest.raises(ValidationError):
            obs.clean()

    def test_rechaza_alumno_no_inscripto_en_comision(self):
        """R-OBS-02: No se puede crear observación sobre alumno que no pertenece a la comisión."""
        periodo = PeriodoLectivo.objects.create(
            codigo="2026-1C",
            nombre="1C 2026",
            fecha_inicio=date(2026, 3, 1),
            fecha_fin=date(2026, 7, 15),
        )
        comision_a = Comision.objects.create(codigo="1A", periodo_lectivo=periodo)
        comision_b = Comision.objects.create(codigo="1B", periodo_lectivo=periodo)
        profesor = Profesor.objects.create(
            identificador_laboral="DOC-502", nombre_completo="Docente"
        )
        AsignacionDocente.objects.create(profesor=profesor, comision=comision_a)

        alumno = Alumno.objects.create(
            identificador_academico="ALU-052", nombre_completo="Alumno de 1B"
        )
        # El alumno está inscripto en 1B, no en 1A
        VinculoAlumnoComision.objects.create(
            alumno=alumno, comision=comision_b, fecha_inscripcion=date(2026, 3, 1)
        )

        obs = ObservacionAcademica(
            alumno=alumno,
            comision=comision_a,
            autor=profesor,
            fecha_hecho_pedagogico=date(2026, 4, 5),
            contenido="Observación indebida",
        )
        with pytest.raises(ValidationError):
            obs.clean()


@pytest.mark.django_db
class TestReglasAsistenciaDominio:
    """Pruebas de reglas de negocio de Asistencia (DEC-004, R-ASI-01, R-ASI-02)."""

    def test_estados_validos_cerrados(self):
        """Solo admite PRESENTE, AUSENTE y TARDE."""
        item1 = AttendanceItem(alumno_id="uuid-1", estado=EstadoAsistencia.PRESENTE)
        item2 = AttendanceItem(alumno_id="uuid-2", estado=EstadoAsistencia.AUSENTE)
        item3 = AttendanceItem(alumno_id="uuid-3", estado=EstadoAsistencia.TARDE)
        assert item1.estado == "PRESENTE"
        assert item2.estado == "AUSENTE"
        assert item3.estado == "TARDE"

        with pytest.raises(AttendanceDomainError):
            AttendanceItem(alumno_id="uuid-4", estado="JUSTIFICADA")

        with pytest.raises(AttendanceDomainError):
            AttendanceItem(alumno_id="uuid-5", estado="MEDIA_FALTA")

    def test_admite_toma_parcial_sin_asumir_ausente(self):
        """R-ASI-02: La toma parcial de asistencia es válida y alumnos sin estado no son AUSENTE."""
        periodo = PeriodoLectivo.objects.create(
            codigo="2026-1C",
            nombre="1C",
            fecha_inicio=date(2026, 3, 1),
            fecha_fin=date(2026, 7, 15),
        )
        comision = Comision.objects.create(codigo="1A", periodo_lectivo=periodo)
        profesor = Profesor.objects.create(
            identificador_laboral="DOC-600", nombre_completo="Docente"
        )
        AsignacionDocente.objects.create(profesor=profesor, comision=comision)

        a1 = Alumno.objects.create(
            identificador_academico="A1", nombre_completo="Alumno Uno"
        )
        a2 = Alumno.objects.create(
            identificador_academico="A2", nombre_completo="Alumno Dos"
        )
        VinculoAlumnoComision.objects.create(
            alumno=a1, comision=comision, fecha_inscripcion=date(2026, 3, 1)
        )
        VinculoAlumnoComision.objects.create(
            alumno=a2, comision=comision, fecha_inscripcion=date(2026, 3, 1)
        )

        clase = InstanciaClase.objects.create(
            comision=comision, docente_registrador=profesor, fecha=date(2026, 4, 10)
        )

        # Se toma asistencia SOLO para a1 (toma parcial)
        lote = [AttendanceItem(alumno_id=str(a1.id), estado=EstadoAsistencia.PRESENTE)]
        resultado = AttendanceService.validar_lote_asistencia(clase, lote)

        assert str(a1.id) in resultado
        assert resultado[str(a1.id)] == "PRESENTE"
        # a2 no está en el resultado y NO fue asignado automáticamente como AUSENTE
        assert str(a2.id) not in resultado
