import type {
  Comision,
  HealthResponse,
  InstanciaClase,
  ItemAsistencia,
  ObservacionAcademica,
  Profesor,
  ResultadoValidacionAsistencia,
  VinculoAlumno,
} from '../types';

/**
 * Cliente de comunicación con la API REST del Sistema Profesor.
 * En desarrollo, si VITE_API_URL no está definido o es relativa, usa /api (proxied por Vite).
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

/**
 * Función auxiliar para realizar peticiones HTTP con manejo estandarizado de errores.
 */
async function request<T>(
  endpoint: string,
  options: RequestInit = {},
  profesorId?: string
): Promise<T> {
  const headers = new Headers(options.headers || {});
  headers.set('Accept', 'application/json');

  if (profesorId) {
    headers.set('X-Profesor-Id', profesorId);
  }

  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  // Si endpoint comienza con / y API_BASE_URL termina con /api, normalizar
  const url = `${API_BASE_URL.replace(/\/$/, '')}/${endpoint.replace(/^\//, '')}`;

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = `Error ${response.status}: ${response.statusText}`;
    try {
      const errorJson = await response.json();
      if (typeof errorJson === 'string') {
        errorDetail = errorJson;
      } else if (Array.isArray(errorJson)) {
        errorDetail = errorJson.join(', ');
      } else if (errorJson && typeof errorJson === 'object') {
        if ('detail' in errorJson && typeof errorJson.detail === 'string') {
          errorDetail = errorJson.detail;
        } else {
          errorDetail = Object.entries(errorJson)
            .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
            .join(' | ');
        }
      }
    } catch {
      // Usar statusText por defecto
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

// ============================================================================
// Servicios de API
// ============================================================================

export async function checkBackendHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('health/');
}

export async function getProfesoresDisponibles(): Promise<Profesor[]> {
  return request<Profesor[]>('profesores/');
}

export async function getPerfilProfesor(profesorId: string): Promise<Profesor> {
  return request<Profesor>('profesor/perfil/', {}, profesorId);
}

export async function getComisionesDocente(
  profesorId: string,
  periodoId?: string
): Promise<Comision[]> {
  const query = periodoId ? `?periodo_id=${encodeURIComponent(periodoId)}` : '';
  return request<Comision[]>(`profesor/comisiones/${query}`, {}, profesorId);
}

export async function getNominaComision(
  profesorId: string,
  comisionId: string,
  incluirBajas: boolean = false
): Promise<VinculoAlumno[]> {
  const query = incluirBajas ? '?incluir_bajas=true' : '';
  return request<VinculoAlumno[]>(
    `comisiones/${comisionId}/alumnos/${query}`,
    {},
    profesorId
  );
}

export async function getClasesComision(
  profesorId: string,
  comisionId: string
): Promise<InstanciaClase[]> {
  return request<InstanciaClase[]>(`comisiones/${comisionId}/clases/`, {}, profesorId);
}

export async function crearClaseComision(
  profesorId: string,
  comisionId: string,
  fecha: string,
  descripcionOpcional: string = ''
): Promise<InstanciaClase> {
  return request<InstanciaClase>(
    `comisiones/${comisionId}/clases/`,
    {
      method: 'POST',
      body: JSON.stringify({
        fecha,
        descripcion_opcional: descripcionOpcional,
      }),
    },
    profesorId
  );
}

export async function getObservacionesComision(
  profesorId: string,
  comisionId: string,
  alumnoId?: string
): Promise<ObservacionAcademica[]> {
  const query = alumnoId ? `?alumno_id=${encodeURIComponent(alumnoId)}` : '';
  return request<ObservacionAcademica[]>(
    `comisiones/${comisionId}/observaciones/${query}`,
    {},
    profesorId
  );
}

export async function crearObservacion(
  profesorId: string,
  comisionId: string,
  alumnoId: string,
  fechaHechoPedagogico: string,
  contenido: string
): Promise<ObservacionAcademica> {
  return request<ObservacionAcademica>(
    `comisiones/${comisionId}/observaciones/`,
    {
      method: 'POST',
      body: JSON.stringify({
        alumno: alumnoId,
        fecha_hecho_pedagogico: fechaHechoPedagogico,
        contenido,
      }),
    },
    profesorId
  );
}

export async function validarLoteAsistencia(
  profesorId: string,
  comisionId: string,
  claseId: string,
  registros: ItemAsistencia[]
): Promise<ResultadoValidacionAsistencia> {
  return request<ResultadoValidacionAsistencia>(
    `comisiones/${comisionId}/clases/${claseId}/asistencia/validar/`,
    {
      method: 'POST',
      body: JSON.stringify(registros),
    },
    profesorId
  );
}
