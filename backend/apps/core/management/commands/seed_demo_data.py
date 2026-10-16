"""
Comando de gestión Django para sembrar datos de demostración para desarrollo.

Uso:
    python manage.py seed_demo_data
"""

from datetime import date

from django.core.management.base import BaseCommand

from apps.core.models import (
    Alumno,
    AsignacionDocente,
    Comision,
    InstanciaClase,
    Materia,
    ObservacionAcademica,
    PeriodoLectivo,
    Profesor,
    VinculoAlumnoComision,
)


class Command(BaseCommand):
    help = "Siembra datos de demostración académicos para el desarrollo local del Módulo Profesor."

    def handle(self, *args, **options):
        self.stdout.write("Sembrando datos de demostración...")

        # 1. Período Lectivo
        periodo, _ = PeriodoLectivo.objects.get_or_create(
            codigo="2026-1C",
            defaults={
                "nombre": "Primer Cuatrimestre 2026",
                "fecha_inicio": date(2026, 3, 1),
                "fecha_fin": date(2026, 7, 15),
                "es_vigente": True,
            },
        )
        if not periodo.es_vigente:
            periodo.es_vigente = True
            periodo.save()

        # 2. Materias
        m_pps, _ = Materia.objects.get_or_create(
            codigo="PPS-301", defaults={"nombre": "Práctica Profesional Supervisada"}
        )
        m_ds, _ = Materia.objects.get_or_create(
            codigo="DS-302", defaults={"nombre": "Desarrollo de Software III"}
        )
        m_bd, _ = Materia.objects.get_or_create(
            codigo="BD-202", defaults={"nombre": "Bases de Datos II"}
        )

        # 3. Profesores
        prof_martin, _ = Profesor.objects.get_or_create(
            identificador_laboral="DOC-101",
            defaults={
                "nombre_completo": "Prof. Martín Albarracín",
                "email": "martin.albarracin@sga.edu.ar",
                "activo": True,
            },
        )
        prof_laura, _ = Profesor.objects.get_or_create(
            identificador_laboral="DOC-102",
            defaults={
                "nombre_completo": "Prof. Laura Benítez",
                "email": "laura.benitez@sga.edu.ar",
                "activo": True,
            },
        )

        # 4. Comisiones
        com_3a, _ = Comision.objects.get_or_create(
            codigo="3A-NOCHE",
            periodo_lectivo=periodo,
            defaults={"descripcion": "3er Año - Turno Noche (18:30 a 22:30)"},
        )
        com_3a.materias.set([m_pps, m_ds])

        com_3b, _ = Comision.objects.get_or_create(
            codigo="3B-TARDE",
            periodo_lectivo=periodo,
            defaults={"descripcion": "3er Año - Turno Tarde (13:30 a 17:30)"},
        )
        com_3b.materias.set([m_pps])

        com_2a, _ = Comision.objects.get_or_create(
            codigo="2A-MANANA",
            periodo_lectivo=periodo,
            defaults={"descripcion": "2do Año - Turno Mañana (08:00 a 12:00)"},
        )
        com_2a.materias.set([m_bd])

        # 5. Asignaciones Docentes
        AsignacionDocente.objects.get_or_create(
            profesor=prof_martin,
            comision=com_3a,
            defaults={"rol_docente": "TITULAR", "activo": True},
        )
        AsignacionDocente.objects.get_or_create(
            profesor=prof_martin,
            comision=com_3b,
            defaults={"rol_docente": "TITULAR", "activo": True},
        )
        AsignacionDocente.objects.get_or_create(
            profesor=prof_laura,
            comision=com_2a,
            defaults={"rol_docente": "TITULAR", "activo": True},
        )

        # 6. Alumnos y Vínculos
        estudiantes = [
            ("ALU-301", "Acuña, Sofía", "sofia.acuna@alumnos.edu.ar"),
            ("ALU-302", "Brizuela, Matías", "matias.brizuela@alumnos.edu.ar"),
            ("ALU-303", "Castillo, Valentina", "valentina.castillo@alumnos.edu.ar"),
            ("ALU-304", "Domínguez, Lucas", "lucas.dominguez@alumnos.edu.ar"),
            ("ALU-305", "Esperanza, Camilo", "camilo.esperanza@alumnos.edu.ar"),
            ("ALU-306", "Fernández, Julieta", "julieta.fernandez@alumnos.edu.ar"),
            ("ALU-307", "García, Tomás", "tomas.garcia@alumnos.edu.ar"),
            ("ALU-308", "Herrera, Micaela", "micaela.herrera@alumnos.edu.ar"),
        ]

        alumnos_objs = {}
        for legajo, nombre, mail in estudiantes:
            alu, _ = Alumno.objects.get_or_create(
                identificador_academico=legajo,
                defaults={"nombre_completo": nombre, "email": mail},
            )
            alumnos_objs[legajo] = alu

        # Vínculos en 3A-NOCHE (activos: ALU-301 a ALU-305)
        for leg in ["ALU-301", "ALU-302", "ALU-303", "ALU-304", "ALU-305"]:
            VinculoAlumnoComision.objects.get_or_create(
                alumno=alumnos_objs[leg],
                comision=com_3a,
                defaults={"fecha_inscripcion": date(2026, 3, 1), "activo": True},
            )

        # Caso límite 2: ALU-306 cursó en 3A hasta el 1 de abril y pasó a 3B
        VinculoAlumnoComision.objects.get_or_create(
            alumno=alumnos_objs["ALU-306"],
            comision=com_3a,
            fecha_inscripcion=date(2026, 3, 1),
            defaults={"fecha_baja": date(2026, 4, 1), "activo": False},
        )
        VinculoAlumnoComision.objects.get_or_create(
            alumno=alumnos_objs["ALU-306"],
            comision=com_3b,
            fecha_inscripcion=date(2026, 4, 2),
            defaults={"activo": True},
        )

        # Vínculos en 3B-TARDE
        for leg in ["ALU-307", "ALU-308"]:
            VinculoAlumnoComision.objects.get_or_create(
                alumno=alumnos_objs[leg],
                comision=com_3b,
                defaults={"fecha_inscripcion": date(2026, 3, 1), "activo": True},
            )

        # 7. Instancia de clase de demostración
        clase_demo, _ = InstanciaClase.objects.get_or_create(
            comision=com_3a,
            fecha=date(2026, 4, 15),
            docente_registrador=prof_martin,
            defaults={"descripcion_opcional": "Sesión teórica y taller de integración"},
        )

        # 8. Observaciones académicas de demostración
        ObservacionAcademica.objects.get_or_create(
            alumno=alumnos_objs["ALU-301"],
            comision=com_3a,
            autor=prof_martin,
            fecha_hecho_pedagogico=date(2026, 4, 10),
            defaults={
                "contenido": "Excelente predisposición y claridad conceptual durante la exposición de arquitectura."
            },
        )
        ObservacionAcademica.objects.get_or_create(
            alumno=alumnos_objs["ALU-302"],
            comision=com_3a,
            autor=prof_martin,
            fecha_hecho_pedagogico=date(2026, 4, 12),
            defaults={
                "contenido": "Se sugiere reforzar la práctica de normalización de modelos relacionales."
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Datos sembrados con éxito:\n"
                f"- Período activo: {periodo.nombre}\n"
                f"- Docentes: {prof_martin.nombre_completo} (DOC-101), {prof_laura.nombre_completo} (DOC-102)\n"
                f"- Comisiones: {com_3a.codigo}, {com_3b.codigo}, {com_2a.codigo}\n"
                f"- Alumnos cargados: {len(estudiantes)}\n"
                f"- Clase demo: {clase_demo.fecha} ({clase_demo.comision.codigo})\n"
            )
        )
