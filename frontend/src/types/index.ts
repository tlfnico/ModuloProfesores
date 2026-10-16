/**
 * Definiciones de tipos base para la aplicación frontend del Módulo Profesor.
 */

export interface HealthResponse {
  status: 'ok' | 'error';
  service: string;
}

export interface ApiError {
  message: string;
  detail?: string;
}
