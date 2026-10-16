import { useState } from 'react';
import { checkBackendHealth } from '../api/client';
import type { HealthResponse } from '../types';

export function StatusCard() {
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCheckHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await checkBackendHealth();
      setHealth(data);
    } catch (err: unknown) {
      setHealth(null);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('No fue posible contactar al backend');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card" aria-labelledby="status-card-title">
      <h2 id="status-card-title" className="card-title">
        Diagnóstico de Conectividad con el Backend
      </h2>
      <p className="card-description">
        Comprueba la disponibilidad del servidor de la API REST local.
      </p>

      <div className="button-group">
        <button
          type="button"
          className="btn btn-primary"
          onClick={handleCheckHealth}
          disabled={loading}
          aria-busy={loading}
        >
          {loading ? 'Consultando...' : 'Comprobar estado del backend'}
        </button>
      </div>

      <div
        className="status-region"
        role="region"
        aria-live="polite"
        aria-atomic="true"
      >
        {health && (
          <div className="alert alert-success" role="status">
            <strong>Conexión exitosa:</strong> El backend respondió correctamente.
            <div className="details-text">
              Servicio: <code>{health.service}</code> | Estado: <code>{health.status}</code>
            </div>
          </div>
        )}

        {error && (
          <div className="alert alert-error" role="alert">
            <strong>Error de conexión:</strong> {error}.
            <p className="hint-text">
              Verificá que el backend esté ejecutándose en <code>http://localhost:8000</code>.
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
