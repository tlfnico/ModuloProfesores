"""
Puertos de arquitectura hexagonal (interfaces abstractas) para el Módulo Profesor.

Define los contratos que desacoplan la lógica de dominio de las dependencias externas
(Autenticación institucional, Datos académicos centrales y Persistencia de asistencia).
Ver docs/ARCHITECTURE.md y docs/DECISIONS.md (DEC-008, DEC-017).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IAuthenticationGateway(ABC):
    """
    Puerto para verificación de identidad y roles de usuario.

    Aísla al dominio del protocolo de autenticación institucional definitivo
    (JWT, OAuth2, cookies de sesión, etc.).
    """

    @abstractmethod
    def get_authenticated_user(self, context: Any) -> Optional[Dict[str, Any]]:
        """Retorna la identidad y rol del usuario autenticado o None."""
        pass


class IAcademicDataGateway(ABC):
    """
    Puerto de solo lectura hacia los datos maestros del SGA Central.

    Permite consultar comisiones asignadas, materias y nómina de alumnos
    garantizando que el Sistema Profesor no altere datos maestros (DEC-006).
    """

    @abstractmethod
    def get_teacher_assignments(self, teacher_id: str) -> List[Dict[str, Any]]:
        """Retorna las comisiones asignadas a un docente en el período activo."""
        pass

    @abstractmethod
    def get_commission_roster(self, commission_id: str) -> List[Dict[str, Any]]:
        """Retorna la nómina de alumnos vinculados a una comisión."""
        pass


class IAttendanceGateway(ABC):
    """
    Puerto para la gestión de asistencia de alumnos.

    Diseñado para soportar tanto el Escenario A (persistencia delegada en el
    Módulo Central de Asistencia) como el Escenario B (persistencia local con
    sincronización institucional) según resolución de DEC-017.
    """

    @abstractmethod
    def register_attendance(
        self, class_instance_id: str, records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Registra la asistencia para una instancia de clase de forma idempotente."""
        pass

    @abstractmethod
    def get_attendance_history(
        self, commission_id: str, student_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Consulta el historial de asistencia registrado."""
        pass


class IObservationRepository(ABC):
    """
    Puerto para el almacenamiento y consulta de observaciones pedagógicas.
    """

    @abstractmethod
    def save_observation(self, observation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Almacena una observación académica asociada a un alumno y comisión."""
        pass

    @abstractmethod
    def list_observations(
        self, student_id: str, commission_id: str
    ) -> List[Dict[str, Any]]:
        """Retorna las observaciones pedagógicas registradas."""
        pass
