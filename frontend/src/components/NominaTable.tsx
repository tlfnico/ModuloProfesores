import { useEffect, useState } from 'react';
import { getNominaComision } from '../api/client';
import type { Comision, Profesor, VinculoAlumno } from '../types';

interface Props {
  profesor: Profesor;
  comision: Comision;
  onSeleccionarAlumnoParaObservacion?: (alumnoId: string) => void;
}

export function NominaTable({
  profesor,
  comision,
  onSeleccionarAlumnoParaObservacion,
}: Props) {
  const [vinculos, setVinculos] = useState<VinculoAlumno[]>([]);
  const [filtroTexto, setFiltroTexto] = useState('');
  const [incluirBajas, setIncluirBajas] = useState(false);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function cargar() {
      setCargando(true);
      setError(null);
      try {
        const data = await getNominaComision(profesor.id, comision.id, incluirBajas);
        setVinculos(data);
      } catch (err: unknown) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError('Error al consultar la nómina de estudiantes');
        }
      } finally {
        setCargando(false);
      }
    }
    cargar();
  }, [profesor.id, comision.id, incluirBajas]);

  const filtrados = vinculos.filter((v) => {
    const termino = filtroTexto.toLowerCase().trim();
    if (!termino) return true;
    const nombre = v.alumno.nombre_completo.toLowerCase();
    const legajo = v.alumno.identificador_academico.toLowerCase();
    return nombre.includes(termino) || legajo.includes(termino);
  });

  return (
    <div className="tab-card-content">
      <div className="panel-intro-header">
        <div>
          <div className="section-category">Funcionalidad F2</div>
          <h3 className="panel-title">
            Nómina de Estudiantes — Comisión {comision.codigo}
          </h3>
          <p className="panel-subtitle">
            Alumnos matriculados bajo la custodia pedagógica de esta comisión. Control estricto de scope docente en servidor.
          </p>
        </div>

        {cargando && (
          <div className="loading-badge" role="status">
            <span className="spinner" aria-hidden="true" /> Cargando nómina...
          </div>
        )}
      </div>

      {error && (
        <div className="alert alert-error" role="alert">
          <strong>Error de consulta:</strong> {error}
        </div>
      )}

      {/* Barra de Filtros y Búsqueda */}
      <div className="table-controls-bar" role="search" aria-label="Filtrar nómina">
        <div className="search-box">
          <span className="search-icon" aria-hidden="true">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
          </span>
          <input
            id="input-filtro-alumnos"
            type="search"
            className="input-search"
            placeholder="Buscar por apellido, nombre o legajo/DNI..."
            value={filtroTexto}
            onChange={(e) => setFiltroTexto(e.target.value)}
            aria-label="Buscar estudiante por nombre o identificador"
          />
          {filtroTexto && (
            <button
              type="button"
              className="btn-clear-search"
              onClick={() => setFiltroTexto('')}
              aria-label="Limpiar búsqueda"
            >
              ✕
            </button>
          )}
        </div>

        <label className="toggle-switch-label">
          <input
            type="checkbox"
            className="toggle-checkbox"
            checked={incluirBajas}
            onChange={(e) => setIncluirBajas(e.target.checked)}
          />
          <span className="toggle-switch-slider" aria-hidden="true" />
          <span className="toggle-text">Incluir bajas (Escenario 2)</span>
        </label>
      </div>

      {/* Estado Vacío */}
      {!cargando && !error && filtrados.length === 0 && (
        <div className="empty-state-box" role="status">
          <div className="empty-icon" aria-hidden="true">🔍</div>
          <h4 className="empty-title">No se encontraron estudiantes</h4>
          <p className="empty-desc">
            {filtroTexto
              ? `No hay coincidencias para "${filtroTexto}". Verificá la ortografía o limpiá el filtro.`
              : 'Esta comisión aún no tiene alumnos inscriptos en este período.'}
          </p>
        </div>
      )}

      {/* Tabla Profesional de Estudiantes */}
      {filtrados.length > 0 && (
        <div className="data-table-container">
          <table className="modern-table" aria-label="Nómina oficial de alumnos">
            <thead>
              <tr>
                <th scope="col" className="th-student">Estudiante</th>
                <th scope="col" className="th-id">Identificador</th>
                <th scope="col" className="th-date">Inscripción</th>
                <th scope="col" className="th-status">Estado</th>
                <th scope="col" className="th-actions text-right">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filtrados.map((v) => {
                const esBaja = !v.activo || Boolean(v.fecha_baja);
                const iniciales = v.alumno.nombre_completo
                  .split(' ')
                  .map((n) => n[0])
                  .slice(0, 2)
                  .join('')
                  .toUpperCase();

                return (
                  <tr key={v.id} className={esBaja ? 'row-inactive' : 'row-active'}>
                    <td className="cell-student-info">
                      <div className="student-profile-cell">
                        <div className="student-avatar" aria-hidden="true">
                          {iniciales}
                        </div>
                        <div className="student-names">
                          <span className="student-fullname">{v.alumno.nombre_completo}</span>
                          {v.alumno.email && (
                            <span className="student-email">{v.alumno.email}</span>
                          )}
                        </div>
                      </div>
                    </td>
                    <td>
                      <code className="legajo-badge">
                        {v.alumno.identificador_academico}
                      </code>
                    </td>
                    <td className="cell-muted-date">
                      {v.fecha_inscripcion}
                    </td>
                    <td>
                      {esBaja ? (
                        <span className="badge-status badge-status-baja" title={`Fecha de baja: ${v.fecha_baja || 'Cese'}`}>
                          Baja ({v.fecha_baja || 'Inactivo'})
                        </span>
                      ) : (
                        <span className="badge-status badge-status-activo">
                          Activo
                        </span>
                      )}
                    </td>
                    <td className="text-right">
                      {onSeleccionarAlumnoParaObservacion && (
                        <button
                          type="button"
                          className="btn btn-sm btn-ghost"
                          onClick={() => onSeleccionarAlumnoParaObservacion(v.alumno.id)}
                          title={`Registrar nota pedagógica para ${v.alumno.nombre_completo}`}
                        >
                          <span aria-hidden="true">📝</span> + Observación
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Pie de Tabla con Totales */}
      <div className="table-summary-bar">
        <span>Total en nómina: <strong>{vinculos.length}</strong></span>
        {filtroTexto && (
          <span>Filtrados: <strong>{filtrados.length}</strong> de {vinculos.length}</span>
        )}
      </div>
    </div>
  );
}
