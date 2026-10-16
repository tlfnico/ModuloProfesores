import { useEffect, useState } from 'react';
import { getProfesoresDisponibles } from '../api/client';
import type { Profesor } from '../types';

interface Props {
  profesorSeleccionado: Profesor | null;
  onSeleccionarProfesor: (profesor: Profesor) => void;
}

export function ProfesorSelector({
  profesorSeleccionado,
  onSeleccionarProfesor,
}: Props) {
  const [profesores, setProfesores] = useState<Profesor[]>([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelado = false;
    async function cargar() {
      setCargando(true);
      setError(null);
      try {
        const data = await getProfesoresDisponibles();
        if (!cancelado) {
          setProfesores(data);
        }
      } catch (err: unknown) {
        if (!cancelado) {
          if (err instanceof Error) {
            setError(err.message);
          } else {
            setError('No fue posible cargar el catálogo de docentes');
          }
        }
      } finally {
        if (!cancelado) {
          setCargando(false);
        }
      }
    }
    cargar();
    return () => {
      cancelado = true;
    };
  }, []);

  useEffect(() => {
    if (profesores.length > 0 && !profesorSeleccionado) {
      onSeleccionarProfesor(profesores[0]);
    }
  }, [profesores, profesorSeleccionado, onSeleccionarProfesor]);

  return (
    <aside className="dev-identity-bar" aria-labelledby="dev-identity-title">
      <div className="dev-identity-content">
        <div className="dev-identity-label-box">
          <span className="dev-pill-badge">Desarrollo</span>
          <div>
            <h2 id="dev-identity-title" className="dev-identity-title">
              Identidad Docente Activa
            </h2>
            <p className="dev-identity-desc">
              Alterná el perfil para evaluar el aislamiento estricto de comisiones en el servidor (R-DOC-01).
            </p>
          </div>
        </div>

        {cargando && (
          <span className="status-indicator status-loading">
            <span className="spinner" aria-hidden="true" /> Cargando catálogo...
          </span>
        )}

        {error && (
          <div className="alert-inline alert-error" role="alert">
            {error}
          </div>
        )}

        {profesores.length > 0 && (
          <div
            className="docentes-switcher-group"
            role="group"
            aria-label="Seleccionar docente para pruebas"
          >
            {profesores.map((prof) => {
              const esActivo = profesorSeleccionado?.id === prof.id;
              return (
                <button
                  key={prof.id}
                  type="button"
                  className={`btn-switcher-pill ${esActivo ? 'btn-switcher-active' : ''}`}
                  onClick={() => onSeleccionarProfesor(prof)}
                  aria-pressed={esActivo}
                >
                  <span className="switcher-indicator" aria-hidden="true">
                    {esActivo ? '●' : '○'}
                  </span>
                  <div className="switcher-text">
                    <span className="switcher-name">{prof.nombre_completo}</span>
                    <span className="switcher-legajo">{prof.identificador_laboral}</span>
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </aside>
  );
}
