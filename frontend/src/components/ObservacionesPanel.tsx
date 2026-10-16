import { useEffect, useState } from 'react';
import { crearObservacion, getNominaComision, getObservacionesComision } from '../api/client';
import type { Comision, ObservacionAcademica, Profesor, VinculoAlumno } from '../types';

interface Props {
  profesor: Profesor;
  comision: Comision;
  alumnoPreseleccionadoId?: string | null;
}

export function ObservacionesPanel({
  profesor,
  comision,
  alumnoPreseleccionadoId,
}: Props) {
  const [observaciones, setObservaciones] = useState<ObservacionAcademica[]>([]);
  const [alumnos, setAlumnos] = useState<VinculoAlumno[]>([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Estado del formulario
  const [alumnoId, setAlumnoId] = useState<string>(alumnoPreseleccionadoId || '');
  const [prevPreseleccionado, setPrevPreseleccionado] = useState(alumnoPreseleccionadoId);
  if (alumnoPreseleccionadoId !== prevPreseleccionado) {
    setPrevPreseleccionado(alumnoPreseleccionadoId);
    if (alumnoPreseleccionadoId) {
      setAlumnoId(alumnoPreseleccionadoId);
    }
  }

  const [fechaHecho, setFechaHecho] = useState<string>(() =>
    new Date().toISOString().split('T')[0]
  );
  const [contenido, setContenido] = useState<string>('');
  const [guardando, setGuardando] = useState(false);
  const [mensajeExito, setMensajeExito] = useState<string | null>(null);

  // Cargar observaciones y nómina
  useEffect(() => {
    let cancelado = false;
    async function cargar() {
      setCargando(true);
      setError(null);
      try {
        const [obsData, nomData] = await Promise.all([
          getObservacionesComision(profesor.id, comision.id),
          getNominaComision(profesor.id, comision.id, true),
        ]);
        if (!cancelado) {
          setObservaciones(obsData);
          setAlumnos(nomData);
          if (nomData.length > 0) {
            setAlumnoId((actual) => actual || nomData[0].alumno.id);
          }
        }
      } catch (err: unknown) {
        if (!cancelado) {
          if (err instanceof Error) {
            setError(err.message);
          } else {
            setError('Error al consultar observaciones');
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
  }, [profesor.id, comision.id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!alumnoId) {
      setError('Debes seleccionar un estudiante destinatario.');
      return;
    }
    if (!contenido.trim()) {
      setError('El comentario de la observación no puede estar vacío.');
      return;
    }

    setGuardando(true);
    setError(null);
    setMensajeExito(null);

    try {
      const nueva = await crearObservacion(
        profesor.id,
        comision.id,
        alumnoId,
        fechaHecho,
        contenido.trim()
      );
      setObservaciones((prev) => [nueva, ...prev]);
      setContenido('');
      setMensajeExito('Observación pedagógica registrada y auditada exitosamente.');
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Error al registrar la observación pedagógica.');
      }
    } finally {
      setGuardando(false);
    }
  };

  return (
    <div className="tab-card-content">
      <div className="panel-intro-header">
        <div>
          <div className="section-category">Funcionalidad F5</div>
          <h3 className="panel-title">
            Observaciones Académicas — Comisión {comision.codigo}
          </h3>
          <p className="panel-subtitle">
            Seguimiento cualitativo y formativo. Registra doble marca temporal inalterable (R-OBS-04).
          </p>
        </div>

        {cargando && (
          <div className="loading-badge" role="status">
            <span className="spinner" aria-hidden="true" /> Actualizando notas...
          </div>
        )}
      </div>

      <div className="observaciones-dashboard-grid">
        {/* Formulario de Nueva Observación */}
        <div className="obs-form-pane">
          <div className="form-card-inner">
            <h4 className="form-card-title">Nueva Observación Formativa</h4>
            <p className="form-card-subtitle">
              Asociá un evento pedagógico observado en clase al historial del estudiante.
            </p>

            <form onSubmit={handleSubmit} className="modern-form" noValidate>
              <div className="form-field">
                <label htmlFor="obs-select-alumno" className="field-label">
                  Estudiante *
                </label>
                <select
                  id="obs-select-alumno"
                  className="input-select"
                  value={alumnoId}
                  onChange={(e) => setAlumnoId(e.target.value)}
                  disabled={guardando || alumnos.length === 0}
                  required
                >
                  {alumnos.length === 0 && <option value="">Sin alumnos disponibles</option>}
                  {alumnos.map((v) => (
                    <option key={v.alumno.id} value={v.alumno.id}>
                      {v.alumno.nombre_completo} ({v.alumno.identificador_academico})
                      {!v.activo ? ' — [Baja]' : ''}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-field">
                <label htmlFor="obs-fecha-hecho" className="field-label">
                  Fecha del Hecho Pedagógico *
                </label>
                <input
                  id="obs-fecha-hecho"
                  type="date"
                  className="input-text"
                  value={fechaHecho}
                  onChange={(e) => setFechaHecho(e.target.value)}
                  disabled={guardando}
                  required
                />
                <span className="field-hint">
                  Fecha en la que ocurrió el hecho en el aula o taller.
                </span>
              </div>

              <div className="form-field">
                <label htmlFor="obs-textarea-contenido" className="field-label">
                  Comentario Pedagógico *
                </label>
                <textarea
                  id="obs-textarea-contenido"
                  rows={4}
                  className="input-textarea"
                  placeholder="Detallá el desempeño, participación, entrega o aspecto formativo relevante..."
                  value={contenido}
                  onChange={(e) => setContenido(e.target.value)}
                  disabled={guardando}
                  required
                />
              </div>

              <div
                className="feedback-box-area"
                role="region"
                aria-live="polite"
                aria-atomic="true"
              >
                {mensajeExito && (
                  <div className="alert-inline alert-success" role="status">
                    ✓ {mensajeExito}
                  </div>
                )}
                {error && (
                  <div className="alert-inline alert-error" role="alert">
                    ⚠ {error}
                  </div>
                )}
              </div>

              <button
                type="submit"
                className="btn btn-primary btn-block"
                disabled={guardando || alumnos.length === 0}
                aria-busy={guardando}
              >
                {guardando ? 'Guardando en servidor...' : 'Registrar Observación'}
              </button>
            </form>
          </div>
        </div>

        {/* Historial de Observaciones */}
        <div className="obs-feed-pane">
          <h4 className="feed-title">
            Historial de Notas Registradas ({observaciones.length})
          </h4>

          {!cargando && observaciones.length === 0 && (
            <div className="empty-state-box" role="status">
              <div className="empty-icon" aria-hidden="true">📝</div>
              <h5 className="empty-title">Sin observaciones en esta comisión</h5>
              <p className="empty-desc">
                Las notas cualitativas que registres quedarán almacenadas aquí cronológicamente.
              </p>
            </div>
          )}

          {observaciones.length > 0 && (
            <div className="obs-feed-list" role="feed" aria-label="Historial de notas formativas">
              {observaciones.map((obs) => (
                <article key={obs.id} className="obs-entry-card">
                  <div className="obs-entry-header">
                    <div className="obs-student-badge">
                      <span className="obs-icon" aria-hidden="true">👤</span>
                      <strong>{obs.alumno_nombre || 'Estudiante'}</strong>
                    </div>

                    <div className="obs-meta-pills">
                      <span className="pill-pedagogic-date" title="Fecha del hecho pedagógico">
                        Hecho: <strong>{obs.fecha_hecho_pedagogico}</strong>
                      </span>
                      <span className="pill-audit-time" title="Marca temporal de auditoría en servidor">
                        Registrado: {new Date(obs.fecha_hora_creacion).toLocaleDateString('es-AR')} {new Date(obs.fecha_hora_creacion).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>

                  <p className="obs-entry-body">{obs.contenido}</p>

                  <div className="obs-entry-footer">
                    <span className="obs-author">
                      Docente: <strong>{obs.autor_nombre || profesor.nombre_completo}</strong>
                    </span>
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
