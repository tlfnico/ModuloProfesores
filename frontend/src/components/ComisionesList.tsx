import { useEffect, useState } from 'react';
import { getComisionesDocente } from '../api/client';
import type { Comision, Profesor } from '../types';

interface Props {
  profesor: Profesor;
  comisionSeleccionada: Comision | null;
  onSeleccionarComision: (comision: Comision) => void;
}

export function ComisionesList({
  profesor,
  comisionSeleccionada,
  onSeleccionarComision,
}: Props) {
  const [comisiones, setComisiones] = useState<Comision[]>([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelado = false;
    async function cargar() {
      setCargando(true);
      setError(null);
      try {
        const data = await getComisionesDocente(profesor.id);
        if (!cancelado) {
          setComisiones(data);
        }
      } catch (err: unknown) {
        if (!cancelado) {
          if (err instanceof Error) {
            setError(err.message);
          } else {
            setError('Error al consultar las comisiones asignadas');
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
  }, [profesor.id]);

  useEffect(() => {
    if (comisiones.length > 0 && !comisionSeleccionada) {
      onSeleccionarComision(comisiones[0]);
    }
  }, [comisiones, comisionSeleccionada, onSeleccionarComision]);

  return (
    <section className="dashboard-section" aria-labelledby="comisiones-heading">
      <div className="section-title-bar">
        <div>
          <div className="section-category">Asignaciones Académicas</div>
          <h2 id="comisiones-heading" className="section-heading">
            Comisiones del Período
          </h2>
          <p className="section-description">
            Comisiones con asignación docente activa en el período lectivo vigente para <strong>{profesor.nombre_completo}</strong> (R-DOC-01).
          </p>
        </div>

        {cargando && (
          <div className="loading-badge" role="status">
            <span className="spinner" aria-hidden="true" /> Actualizando...
          </div>
        )}
      </div>

      {error && (
        <div className="alert alert-error" role="alert">
          <strong>Error de consulta:</strong> {error}
        </div>
      )}

      {!cargando && !error && comisiones.length === 0 && (
        <div className="empty-state-box" role="status">
          <div className="empty-icon" aria-hidden="true">📋</div>
          <h3 className="empty-title">Sin comisiones asignadas</h3>
          <p className="empty-desc">
            No se registran comisiones asignadas a este docente para el período activo.
          </p>
        </div>
      )}

      {comisiones.length > 0 && (
        <div
          className="comisiones-grid-layout"
          role="list"
          aria-label="Listado de comisiones asignadas"
        >
          {comisiones.map((com) => {
            const esActiva = comisionSeleccionada?.id === com.id;
            return (
              <article
                key={com.id}
                role="listitem"
                className={`commission-card ${esActiva ? 'commission-card-selected' : ''}`}
              >
                <div className="commission-card-top">
                  <div className="commission-code-badge">
                    {com.codigo}
                  </div>
                  <span className="period-badge">
                    {com.periodo_lectivo.nombre}
                  </span>
                </div>

                <div className="commission-body">
                  <h3 className="commission-name">
                    {com.descripcion || `Comisión ${com.codigo}`}
                  </h3>

                  <div className="commission-subjects-section">
                    <span className="subjects-heading">Materias asociadas:</span>
                    <div className="subject-tags-container">
                      {com.materias.map((m) => (
                        <span key={m.id} className="subject-pill">
                          {m.nombre} <span className="subject-code">({m.codigo})</span>
                        </span>
                      ))}
                      {com.materias.length === 0 && (
                        <span className="text-muted-italic">Sin materias cargadas</span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="commission-footer">
                  <button
                    type="button"
                    className={`btn ${esActiva ? 'btn-primary' : 'btn-outline'} btn-block`}
                    onClick={() => onSeleccionarComision(com)}
                    aria-pressed={esActiva}
                  >
                    {esActiva ? '✓ Comisión Activa' : 'Gestionar Comisión'}
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
