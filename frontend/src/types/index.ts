/**
 * Definiciones de tipos base para la aplicación frontend del Módulo Profesor.
 * Alineado con SPEC-002 v1.1 y los contratos REST del backend.
 */

export interface HealthResponse {
  status: 'ok' | 'error';
  service: string;
}

export interface Profesor {
  id: string;
  identificador_laboral: string;
  nombre_completo: string;
  email: string;
  activo: boolean;
}

export interface PeriodoLectivo {
  id: string;
  codigo: string;
  nombre: string;
  fecha_inicio: string;
  fecha_fin: string;
  es_vigente: boolean;
}

export interface Materia {
  id: string;
  codigo: string;
  nombre: string;
}

export interface Comision {
  id: string;
  codigo: string;
  descripcion: string;
  periodo_lectivo: PeriodoLectivo;
  materias: Materia[];
}

export interface Alumno {
  id: string;
  identificador_academico: string;
  nombre_completo: string;
  email: string;
}

export interface VinculoAlumno {
  id: string;
  alumno: Alumno;
  fecha_inscripcion: string;
  fecha_baja: string | null;
  activo: boolean;
}

export interface InstanciaClase {
  id: string;
  comision: string;
  docente_registrador: string;
  fecha: string;
  descripcion_opcional: string;
  fecha_hora_registro: string;
}

export interface ObservacionAcademica {
  id: string;
  comision: string;
  alumno: string;
  alumno_nombre: string;
  autor: string;
  autor_nombre: string;
  fecha_hecho_pedagogico: string;
  contenido: string;
  fecha_hora_creacion: string;
}

export type EstadoAsistencia = 'PRESENTE' | 'AUSENTE' | 'TARDE';

export interface ItemAsistencia {
  alumno_id: string;
  estado: EstadoAsistencia;
}

export interface ResultadoValidacionAsistencia {
  valido: boolean;
  comision_codigo: string;
  instancia_clase_id: string;
  fecha_clase: string;
  resumen: {
    total_nomina: number;
    marcados: number;
    presentes: number;
    ausentes: number;
    tardes: number;
    sin_marcar: number;
  };
  es_toma_parcial: boolean;
  estado_persistencia: string;
  mensaje: string;
  registros_validados: Record<string, EstadoAsistencia>;
}

export interface ApiError {
  message: string;
  detail?: string;
}
