"""
Pruebas automatizadas de la API REST del Módulo Profesor.
Valida autorización estricta en servidor (Scope Docente Zero Trust, R-DOC-01).
"""

from datetime import date

import pytest
from django.test import Client

from apps.core.models import (
    Alumno,
    AsignacionDocente,
    Comision,
    InstanciaClase,
    Materia,
    PeriodoLectivo,
    Profesor,
    VinculoAlumnoComision,
)


@pytest.fixture
def setup_datos_academicos():
    """Fixture con estructura docente y comisiones para pruebas."""
    periodo_activo = PeriodoLectivo.objects.create(
        codigo="2026-1C",
        nombre="1er Cuatrimestre 2026",
        fecha_inicio=date(2026, 3, 1),
        fecha_fin=date(2026, 7, 15),
        es_vigente=True,
    )
    periodo_inactivo = PeriodoLectivo.objects.create(
        codigo="2025-2C",
        nombre="2do Cuatrimestre 2025",
        fecha_inicio=date(2025, 8, 1),
        fecha_fin=date(2025, 12, 15),
        es_vigente=False,
    )

    materia = Materia.objects.create(codigo="PROG-3", nombre="Programación III")

    # Comisiones
    comision_asignada = Comision.objects.create(
        codigo="3A-NOCHE", periodo_lectivo=periodo_activo
    )
    comision_asignada.materias.add(materia)

    comision_otra = Comision.objects.create(
        codigo="3B-MANANA", periodo_lectivo=periodo_activo
    )
    comision_otra.materias.add(materia)

    comision_pasada = Comision.objects.create(
        codigo="2A-VIEJA", periodo_lectivo=periodo_inactivo
    )

    # Docente titular
    profesor = Profesor.objects.create(
        identificador_laboral="DOC-100",
        nombre_completo="Profesor Titular",
        email="titular@institucion.edu.ar",
    )
    # Docente ajeno
    profesor_ajeno = Profesor.objects.create(
        identificador_laboral="DOC-999",
        nombre_completo="Profesor Ajeno",
        email="ajeno@institucion.edu.ar",
    )

    # Asignaciones
    AsignacionDocente.objects.create(
        profesor=profesor,
        comision=comision_asignada,
        rol_docente="TITULAR",
        activo=True,
    )
    AsignacionDocente.objects.create(
        profesor=profesor, comision=comision_pasada, rol_docente="TITULAR", activo=True
    )
    AsignacionDocente.objects.create(
        profesor=profesor_ajeno,
        comision=comision_otra,
        rol_docente="TITULAR",
        activo=True,
    )

    # Alumnos
    alumno_1 = Alumno.objects.create(
        identificador_academico="ALU-1001",
        nombre_completo="Estudiante Uno",
        email="alu1@institucion.edu.ar",
    )
    alumno_2 = Alumno.objects.create(
        identificador_academico="ALU-1002",
        nombre_completo="Estudiante Dos",
        email="alu2@institucion.edu.ar",
    )
    VinculoAlumnoComision.objects.create(
        alumno=alumno_1,
        comision=comision_asignada,
        fecha_inscripcion=date(2026, 3, 1),
        activo=True,
    )
    VinculoAlumnoComision.objects.create(
        alumno=alumno_2,
        comision=comision_asignada,
        fecha_inscripcion=date(2026, 3, 1),
        fecha_baja=date(2026, 4, 1),
        activo=False,
    )

    return {
        "periodo_activo": periodo_activo,
        "periodo_inactivo": periodo_inactivo,
        "comision_asignada": comision_asignada,
        "comision_otra": comision_otra,
        "comision_pasada": comision_pasada,
        "profesor": profesor,
        "profesor_ajeno": profesor_ajeno,
        "alumno_1": alumno_1,
        "alumno_2": alumno_2,
    }


@pytest.mark.django_db
class TestComisionesDocenteAPI:
    """F1 — Consulta de comisiones asignadas al docente autenticado."""

    def test_requiere_identificacion_docente(self, client: Client):
        """Retorna 403 si no se envía la cabecera X-Profesor-Id."""
        response = client.get("/api/profesor/comisiones/")
        assert response.status_code == 403

    def test_lista_solo_comisiones_asignadas_en_periodo_activo(
        self, client: Client, setup_datos_academicos
    ):
        """R-DOC-01: El docente solo recibe sus comisiones asignadas del período activo."""
        data = setup_datos_academicos
        docente = data["profesor"]

        response = client.get(
            "/api/profesor/comisiones/",
            HTTP_X_PROFESOR_ID=str(docente.id),
        )
        assert response.status_code == 200
        resultados = response.json()

        # Solo debe figurar 3A-NOCHE (la del período activo), no 3B-MANANA (de otro) ni 2A-VIEJA
        assert len(resultados) == 1
        assert resultados[0]["codigo"] == "3A-NOCHE"
        assert resultados[0]["materias"][0]["codigo"] == "PROG-3"


@pytest.mark.django_db
class TestNominaComisionAPI:
    """F2 — Consulta de nómina de alumnos con verificación de Scope Docente."""

    def test_docente_autorizado_puede_consultar_nomina(
        self, client: Client, setup_datos_academicos
    ):
        """El docente titular consulta la nómina activa de su comisión."""
        data = setup_datos_academicos
        docente = data["profesor"]
        comision = data["comision_asignada"]

        response = client.get(
            f"/api/comisiones/{comision.id}/alumnos/",
            HTTP_X_PROFESOR_ID=str(docente.id),
        )
        assert response.status_code == 200
        nomina = response.json()
        # Por defecto solo trae activos (alumno_1)
        assert len(nomina) == 1
        assert nomina[0]["alumno"]["identificador_academico"] == "ALU-1001"

    def test_docente_no_asignado_recibe_403_forbidden(
        self, client: Client, setup_datos_academicos
    ):
        """R-DOC-01 / Zero Trust: El docente ajeno tiene el acceso bloqueado."""
        data = setup_datos_academicos
        docente_ajeno = data["profesor_ajeno"]
        comision = data["comision_asignada"]

        response = client.get(
            f"/api/comisiones/{comision.id}/alumnos/",
            HTTP_X_PROFESOR_ID=str(docente_ajeno.id),
        )
        assert response.status_code == 403
        assert "Acceso denegado" in response.json()["detail"]


@pytest.mark.django_db
class TestInstanciasClaseAPI:
    """Pruebas de creación y listado de clases pedagógicas."""

    def test_creacion_exitosa_de_clase(self, client: Client, setup_datos_academicos):
        """El docente asignado puede registrar una instancia de clase."""
        data = setup_datos_academicos
        docente = data["profesor"]
        comision = data["comision_asignada"]

        payload = {
            "fecha": "2026-04-15",
            "descripcion_opcional": "Práctica de laboratorio",
        }
        response = client.post(
            f"/api/comisiones/{comision.id}/clases/",
            data=payload,
            content_type="application/json",
            HTTP_X_PROFESOR_ID=str(docente.id),
        )
        assert response.status_code == 201
        res_data = response.json()
        assert res_data["fecha"] == "2026-04-15"
        assert res_data["descripcion_opcional"] == "Práctica de laboratorio"
        assert res_data["docente_registrador"] == str(docente.id)


@pytest.mark.django_db
class TestObservacionesAcademicasAPI:
    """F5 — Registro y consulta de observaciones pedagógicas."""

    def test_crear_y_listar_observacion_valida(
        self, client: Client, setup_datos_academicos
    ):
        """El docente registra una observación con fecha de hecho pedagógico."""
        data = setup_datos_academicos
        docente = data["profesor"]
        comision = data["comision_asignada"]
        alumno = data["alumno_1"]

        payload = {
            "alumno": str(alumno.id),
            "fecha_hecho_pedagogico": "2026-04-10",
            "contenido": "Excelente participación en el debate teórico.",
        }
        response = client.post(
            f"/api/comisiones/{comision.id}/observaciones/",
            data=payload,
            content_type="application/json",
            HTTP_X_PROFESOR_ID=str(docente.id),
        )
        assert response.status_code == 201
        creada = response.json()
        assert creada["contenido"] == payload["contenido"]
        assert creada["fecha_hecho_pedagogico"] == "2026-04-10"
        assert creada["autor_nombre"] == docente.nombre_completo

        # Listar observaciones de la comisión
        list_resp = client.get(
            f"/api/comisiones/{comision.id}/observaciones/",
            HTTP_X_PROFESOR_ID=str(docente.id),
        )
        assert list_resp.status_code == 200
        assert len(list_resp.json()) == 1

    def test_rechaza_observacion_para_docente_ajeno(
        self, client: Client, setup_datos_academicos
    ):
        """Un docente ajeno no puede registrar observaciones en una comisión ajena."""
        data = setup_datos_academicos
        docente_ajeno = data["profesor_ajeno"]
        comision = data["comision_asignada"]
        alumno = data["alumno_1"]

        payload = {
            "alumno": str(alumno.id),
            "fecha_hecho_pedagogico": "2026-04-10",
            "contenido": "Intento no autorizado.",
        }
        response = client.post(
            f"/api/comisiones/{comision.id}/observaciones/",
            data=payload,
            content_type="application/json",
            HTTP_X_PROFESOR_ID=str(docente_ajeno.id),
        )
        assert response.status_code == 403


@pytest.mark.django_db
class TestProfesoresYPerfilAPI:
    """Pruebas de endpoints auxiliares de profesores y perfil."""

    def test_listar_profesores_activos(self, client: Client, setup_datos_academicos):
        response = client.get("/api/profesores/")
        assert response.status_code == 200
        profesores = response.json()
        assert len(profesores) >= 2

    def test_perfil_profesor_autenticado(self, client: Client, setup_datos_academicos):
        data = setup_datos_academicos
        docente = data["profesor"]
        response = client.get(
            "/api/profesor/perfil/",
            HTTP_X_PROFESOR_ID=str(docente.id),
        )
        assert response.status_code == 200
        perfil = response.json()
        assert perfil["id"] == str(docente.id)
        assert perfil["identificador_laboral"] == "DOC-100"


@pytest.mark.django_db
class TestValidacionAsistenciaAPI:
    """F3 / F4 — Validación áulica de asistencia en servidor (DEC-017, R-ASI-01 a R-ASI-03)."""

    def test_valida_lote_asistencia_y_reporta_toma_parcial(
        self, client: Client, setup_datos_academicos
    ):
        data = setup_datos_academicos
        docente = data["profesor"]
        comision = data["comision_asignada"]
        alumno = data["alumno_1"]

        clase = InstanciaClase.objects.create(
            comision=comision,
            docente_registrador=docente,
            fecha=date(2026, 4, 15),
            descripcion_opcional="Clase regular",
        )

        payload = [{"alumno_id": str(alumno.id), "estado": "PRESENTE"}]
        response = client.post(
            f"/api/comisiones/{comision.id}/clases/{clase.id}/asistencia/validar/",
            data=payload,
            content_type="application/json",
            HTTP_X_PROFESOR_ID=str(docente.id),
        )
        assert response.status_code == 200
        res = response.json()
        assert res["valido"] is True
        assert res["resumen"]["presentes"] == 1
        assert "DEC-017" in res["estado_persistencia"]

    def test_rechaza_docente_no_asignado(self, client: Client, setup_datos_academicos):
        data = setup_datos_academicos
        docente_ajeno = data["profesor_ajeno"]
        comision = data["comision_asignada"]
        docente = data["profesor"]

        clase = InstanciaClase.objects.create(
            comision=comision,
            docente_registrador=docente,
            fecha=date(2026, 4, 15),
        )
        response = client.post(
            f"/api/comisiones/{comision.id}/clases/{clase.id}/asistencia/validar/",
            data=[],
            content_type="application/json",
            HTTP_X_PROFESOR_ID=str(docente_ajeno.id),
        )
        assert response.status_code == 403
