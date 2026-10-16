"""
Pruebas exhaustivas de seguridad, permisos y robustez ante manipulación de IDs.
Verifica que las restricciones de Scope Docente (R-DOC-01) y reglas de negocio
se cumplan inquebrantablemente a nivel de servidor (Zero Trust).
"""

import uuid
from datetime import date

import pytest
from rest_framework import status
from rest_framework.test import APIClient

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
def api_client():
    return APIClient()


@pytest.fixture
def setup_robustness_data():
    """Configura dos profesores con comisiones disjuntas y alumnos diferenciados."""
    periodo = PeriodoLectivo.objects.create(
        codigo="2026-ROB",
        nombre="Período Robustez 2026",
        fecha_inicio=date(2026, 3, 1),
        fecha_fin=date(2026, 7, 31),
        es_vigente=True,
    )

    profesor_a = Profesor.objects.create(
        identificador_laboral="DOC-ROB-A",
        nombre_completo="Docente Autorizado A",
        email="docente.a@sga.edu.ar",
    )
    profesor_b = Profesor.objects.create(
        identificador_laboral="DOC-ROB-B",
        nombre_completo="Docente Ajeno B",
        email="docente.b@sga.edu.ar",
    )

    materia = Materia.objects.create(codigo="MAT-ROB", nombre="Materia de Prueba")

    # Comisión 1 -> Asignada a Profesor A
    comision_a = Comision.objects.create(codigo="COM-A", periodo_lectivo=periodo)
    comision_a.materias.add(materia)
    AsignacionDocente.objects.create(
        profesor=profesor_a, comision=comision_a, rol_docente="TITULAR", activo=True
    )

    # Comisión 2 -> Asignada a Profesor B
    comision_b = Comision.objects.create(codigo="COM-B", periodo_lectivo=periodo)
    comision_b.materias.add(materia)
    AsignacionDocente.objects.create(
        profesor=profesor_b, comision=comision_b, rol_docente="TITULAR", activo=True
    )

    # Alumno 1 en Comisión A
    alumno_a = Alumno.objects.create(
        identificador_academico="ALU-A-01",
        nombre_completo="Estudiante Comisión A",
        email="alumno.a@sga.edu.ar",
    )
    VinculoAlumnoComision.objects.create(
        alumno=alumno_a,
        comision=comision_a,
        fecha_inscripcion=date(2026, 3, 1),
        activo=True,
    )

    # Alumno 2 en Comisión B
    alumno_b = Alumno.objects.create(
        identificador_academico="ALU-B-01",
        nombre_completo="Estudiante Comisión B",
        email="alumno.b@sga.edu.ar",
    )
    VinculoAlumnoComision.objects.create(
        alumno=alumno_b,
        comision=comision_b,
        fecha_inscripcion=date(2026, 3, 1),
        activo=True,
    )

    # Instancia de clase para Comisión A
    clase_a = InstanciaClase.objects.create(
        comision=comision_a,
        docente_registrador=profesor_a,
        fecha=date(2026, 4, 10),
        descripcion_opcional="Clase Comisión A",
    )

    # Instancia de clase para Comisión B
    clase_b = InstanciaClase.objects.create(
        comision=comision_b,
        docente_registrador=profesor_b,
        fecha=date(2026, 4, 10),
        descripcion_opcional="Clase Comisión B",
    )

    return {
        "periodo": periodo,
        "profesor_a": profesor_a,
        "profesor_b": profesor_b,
        "comision_a": comision_a,
        "comision_b": comision_b,
        "alumno_a": alumno_a,
        "alumno_b": alumno_b,
        "clase_a": clase_a,
        "clase_b": clase_b,
    }


@pytest.mark.django_db
class TestScopeDocenteZeroTrust:
    """Verifica el principio de mínimo privilegio y aislamiento de comisiones."""

    def test_acceso_sin_cabecera_o_con_id_inexistente_retorna_403(
        self, api_client, setup_robustness_data
    ):
        data = setup_robustness_data
        url = f"/api/comisiones/{data['comision_a'].id}/alumnos/"

        # Sin cabecera
        res_sin_cabecera = api_client.get(url)
        assert res_sin_cabecera.status_code == status.HTTP_403_FORBIDDEN

        # Con ID inexistente
        res_id_falso = api_client.get(url, HTTP_X_PROFESOR_ID=str(uuid.uuid4()))
        assert res_id_falso.status_code == status.HTTP_403_FORBIDDEN

    def test_docente_no_puede_consultar_nomina_de_otra_comision(
        self, api_client, setup_robustness_data
    ):
        """Profesor A intenta ver nómina de Comisión B."""
        data = setup_robustness_data
        url = f"/api/comisiones/{data['comision_b'].id}/alumnos/"

        res = api_client.get(
            url, HTTP_X_PROFESOR_ID=data["profesor_a"].identificador_laboral
        )
        assert res.status_code == status.HTTP_403_FORBIDDEN
        assert "Acceso denegado" in res.data["detail"]

    def test_docente_no_puede_crear_clase_en_otra_comision(
        self, api_client, setup_robustness_data
    ):
        """Profesor A intenta registrar clase en Comisión B."""
        data = setup_robustness_data
        url = f"/api/comisiones/{data['comision_b'].id}/clases/"

        res = api_client.post(
            url,
            {"fecha": "2026-04-15", "descripcion_opcional": "Intento no autorizado"},
            format="json",
            HTTP_X_PROFESOR_ID=str(data["profesor_a"].id),
        )
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_docente_no_puede_consultar_ni_crear_observaciones_en_otra_comision(
        self, api_client, setup_robustness_data
    ):
        """Profesor A intenta operar observaciones en Comisión B."""
        data = setup_robustness_data
        url = f"/api/comisiones/{data['comision_b'].id}/observaciones/"

        # GET
        res_get = api_client.get(url, HTTP_X_PROFESOR_ID=str(data["profesor_a"].id))
        assert res_get.status_code == status.HTTP_403_FORBIDDEN

        # POST
        res_post = api_client.post(
            url,
            {
                "alumno": str(data["alumno_b"].id),
                "fecha_hecho_pedagogico": "2026-04-10",
                "contenido": "Intento de observación indebida",
            },
            format="json",
            HTTP_X_PROFESOR_ID=str(data["profesor_a"].id),
        )
        assert res_post.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestValidacionAsistenciaRobustez:
    """Verifica resistencia ante manipulación de IDs de clases, alumnos y estados en asistencia."""

    def test_rechaza_clase_que_pertenece_a_otra_comision_id_manipulado(
        self, api_client, setup_robustness_data
    ):
        """Docente A envía la URL de su comisión pero el UUID de una clase de la comisión B."""
        data = setup_robustness_data
        url = f"/api/comisiones/{data['comision_a'].id}/clases/{data['clase_b'].id}/asistencia/validar/"

        payload = [{"alumno_id": str(data["alumno_a"].id), "estado": "PRESENTE"}]

        res = api_client.post(
            url, payload, format="json", HTTP_X_PROFESOR_ID=str(data["profesor_a"].id)
        )
        # La clase no pertenece a la comisión A -> 404
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_rechaza_alumno_que_pertenece_a_otra_comision_en_lote(
        self, api_client, setup_robustness_data
    ):
        """Docente A intenta incluir a Alumno B (de otra comisión) en la toma de Comisión A."""
        data = setup_robustness_data
        url = f"/api/comisiones/{data['comision_a'].id}/clases/{data['clase_a'].id}/asistencia/validar/"

        payload = [
            {"alumno_id": str(data["alumno_a"].id), "estado": "PRESENTE"},
            {"alumno_id": str(data["alumno_b"].id), "estado": "PRESENTE"},
        ]

        res = api_client.post(
            url, payload, format="json", HTTP_X_PROFESOR_ID=str(data["profesor_a"].id)
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert "no pertenece activamente" in res.data["detail"]

    def test_rechaza_estado_invalido_en_lote(self, api_client, setup_robustness_data):
        data = setup_robustness_data
        url = f"/api/comisiones/{data['comision_a'].id}/clases/{data['clase_a'].id}/asistencia/validar/"

        payload = [{"alumno_id": str(data["alumno_a"].id), "estado": "JUSTIFICADO"}]

        res = api_client.post(
            url, payload, format="json", HTTP_X_PROFESOR_ID=str(data["profesor_a"].id)
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_rechaza_alumno_duplicado_en_mismo_lote(
        self, api_client, setup_robustness_data
    ):
        data = setup_robustness_data
        url = f"/api/comisiones/{data['comision_a'].id}/clases/{data['clase_a'].id}/asistencia/validar/"

        payload = [
            {"alumno_id": str(data["alumno_a"].id), "estado": "PRESENTE"},
            {"alumno_id": str(data["alumno_a"].id), "estado": "AUSENTE"},
        ]

        res = api_client.post(
            url, payload, format="json", HTTP_X_PROFESOR_ID=str(data["profesor_a"].id)
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert "duplicado" in res.data["detail"]

    def test_rechaza_lote_vacio_y_tipo_invalido(
        self, api_client, setup_robustness_data
    ):
        data = setup_robustness_data
        url = f"/api/comisiones/{data['comision_a'].id}/clases/{data['clase_a'].id}/asistencia/validar/"

        # Lista vacía
        res_vacio = api_client.post(
            url, [], format="json", HTTP_X_PROFESOR_ID=str(data["profesor_a"].id)
        )
        assert res_vacio.status_code == status.HTTP_400_BAD_REQUEST

        # Objeto en lugar de lista
        res_no_lista = api_client.post(
            url, {}, format="json", HTTP_X_PROFESOR_ID=str(data["profesor_a"].id)
        )
        assert res_no_lista.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestObservacionesRobustez:
    """Verifica reglas de negocio de observaciones y consistencia de autoría."""

    def test_rechaza_observacion_para_alumno_ajeno_a_la_comision(
        self, api_client, setup_robustness_data
    ):
        """Docente A intenta registrar observación a Alumno B en Comisión A."""
        data = setup_robustness_data
        url = f"/api/comisiones/{data['comision_a'].id}/observaciones/"

        payload = {
            "alumno": str(data["alumno_b"].id),
            "fecha_hecho_pedagogico": "2026-04-10",
            "contenido": "Nota para alumno no matriculado",
        }

        res = api_client.post(
            url, payload, format="json", HTTP_X_PROFESOR_ID=str(data["profesor_a"].id)
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert "alumno" in str(res.data)

    def test_servidor_fija_autor_autenticado_e_ignora_suplantacion_en_payload(
        self, api_client, setup_robustness_data
    ):
        """Payload intenta enviar autor=profesor_b, pero el servidor debe forzar profesor_a."""
        data = setup_robustness_data
        url = f"/api/comisiones/{data['comision_a'].id}/observaciones/"

        payload = {
            "alumno": str(data["alumno_a"].id),
            "autor": str(data["profesor_b"].id),  # intento de suplantación
            "fecha_hecho_pedagogico": "2026-04-10",
            "contenido": "Nota legítima de desempeño",
        }

        res = api_client.post(
            url, payload, format="json", HTTP_X_PROFESOR_ID=str(data["profesor_a"].id)
        )
        assert res.status_code == status.HTTP_201_CREATED
        assert str(res.data["autor"]) == str(data["profesor_a"].id)
        assert res.data["autor_nombre"] == data["profesor_a"].nombre_completo

    def test_consulta_con_periodo_id_y_alumno_id_invalidos_no_produce_500(
        self, api_client, setup_robustness_data
    ):
        data = setup_robustness_data

        # periodo_id inválido
        res_periodo = api_client.get(
            "/api/profesor/comisiones/?periodo_id=formato-invalido-xyz",
            HTTP_X_PROFESOR_ID=str(data["profesor_a"].id),
        )
        assert res_periodo.status_code == status.HTTP_404_NOT_FOUND

        # alumno_id no-UUID en observaciones
        res_obs = api_client.get(
            f"/api/comisiones/{data['comision_a'].id}/observaciones/?alumno_id=no-es-uuid",
            HTTP_X_PROFESOR_ID=str(data["profesor_a"].id),
        )
        assert res_obs.status_code == status.HTTP_200_OK
        assert len(res_obs.data) == 0
