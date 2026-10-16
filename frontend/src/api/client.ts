import type { HealthResponse } from '../types';

/**
 * Cliente de comunicación con la API del Backend.
 * Lee la URL base desde la variable de entorno VITE_API_URL.
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export async function checkBackendHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health/`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`El servidor respondió con código HTTP ${response.status}`);
  }

  return response.json();
}
