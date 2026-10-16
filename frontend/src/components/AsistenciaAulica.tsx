import { useEffect, useState } from 'react';
import {
  crearClaseComision,
  getClasesComision,
  getNominaComision,
  validarLoteAsistencia,
} from '../api/client';
import type {
  Comision,
  EstadoAsistencia,
  InstanciaClase,
  ItemAsistencia,
  Profesor,
  ResultadoValidacionAsistencia,
  VinculoAlumno,
} from '../types';

interface Props {
  profesor: Profesor;
  comision: Comision;
}

export function AsistenciaAulica({ profesor, comision }: Props) {
  // Lista de clases de la comisión
  const [clases, setClases] = useState<InstanciaClase[]>([]);
  const [claseSeleccionadaId, setClaseSeleccionadaId] = useState<string>('');
  const [cargandoClases, setCargandoClases] = useState(false);

  // Formulario para nueva clase
  const [mostrarNuevaClase, setMostrarNuevaClase] = useState(false);
  const [nuevaFecha, setNuevaFecha] = useState<string>(() =>
    new Date().toISOString().split('T')[0]
  );
  const [nuevaDescripcion, setNuevaDescripcion] = useState<string>('');
  const [creandoClase, setCreandoClase] = useState(false);

  // Nómina de alumnos activos para la asistencia
  const [nomina, setNomina] = useState<VinculoAlumno[]>([]);
  const [cargandoNomina, setCargandoNomina] = useState(false);

  // Estado local de asistencia: { [alumnoId]: 'PRESENTE' | 'AUSENTE' | 'TARDE' }
  const [marcas, setMarcas] = useState<Record<string, EstadoAsistencia>>({});

  // Validación en servidor
  const [validando, setValidando] = useState(false);
  const [resultadoValidacion, setResultadoValidacion] =
    useState<ResultadoValidacionAsistencia | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Cargar clases y nómina de la comisión
  useEffect(() => {
    async function inicializar() {
      setCargandoClases(true);
      setCargandoNomina(true);
      setError(null);
      setResultadoValidacion(null);
      setMarcas({});

      try {
        const [clasesData, nominaData] = await Promise.all([
          getClasesComision(profesor.id, comision.id),
          getNominaComision(profesor.id, comision.id, false), // solo activos
        ]);

        setClases(clasesData);
        if (clasesData.length > 0) {
          setClaseSeleccionadaId(clasesData[0].id);
        } else {
          setClaseSeleccionadaId('');
        }

        setNomina(nominaData);
      } catch (err: unknown) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError('Error al cargar datos para la toma de asistencia');
        }
      } finally {
        setCargandoClases(false);
        setCargandoNomina(false);
      }
    }

    inicializar();
  }, [profesor.id, comision.id]);

  // Manejar creación de clase
  const handleCrearClase = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nuevaFecha) {
      setError('Debes especificar una fecha válida.');
      return;
    }

    setCreandoClase(true);
    setError(null);

    try {
      const claseCreada = await crearClaseComision(
        profesor.id,
        comision.id,
        nuevaFecha,
        nuevaDescripcion.trim()
      );
      setClases((prev) => [claseCreada, ...prev]);
      setClaseSeleccionadaId(claseCreada.id);
      setMostrarNuevaClase(false);
      setNuevaDescripcion('');
      setResultadoValidacion(null);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Error al crear la instancia de clase');
      }
    } finally {
      setCreandoClase(false);
    }
  };

  // Marcar estado individual de un alumno
  const handleMarcar = (alumnoId: string, estado: EstadoAsistencia) => {
    setMarcas((prev) => {
      if (prev[alumnoId] === estado) {
        const nuevo = { ...prev };
        delete nuevo[alumnoId];
        return nuevo;
      }
      return {
        ...prev,
        [alumnoId]: estado,
      };
    });
    setResultadoValidacion(null);
  };

  // Acciones rápidas
  const handleMarcarTodosPresentes = () => {
    const nuevo: Record<string, EstadoAsistencia> = {};
    for (const v of nomina) {
      nuevo[v.alumno.id] = 'PRESENTE';
    }
    setMarcas(nuevo);
    setResultadoValidacion(null);
  };

  const handleLimpiarMarcas = () => {
    setMarcas({});
    setResultadoValidacion(null);
  };

  // Contadores calculados
  const totalAlumnos = nomina.length;
  const marcadosCount = Object.keys(marcas).length;
  const presentesCount = Object.values(marcas).filter((e) => e === 'PRESENTE').length;
  const ausentesCount = Object.values(marcas).filter((e) => e === 'AUSENTE').length;
  const tardesCount = Object.values(marcas).filter((e) => e === 'TARDE').length;
  const sinMarcarCount = totalAlumnos - marcadosCount;

  // Enviar validación al backend
  const handleValidarAsistencia = async () => {
    if (!claseSeleccionadaId) {
      setError('Debes seleccionar o crear una sesión de clase antes de validar.');
      return;
    }

    if (marcadosCount === 0) {
      setError('Debes marcar el estado de asistencia de al menos un estudiante.');
      return;
    }

    setValidando(true);
    setError(null);
    setResultadoValidacion(null);

    const registros: ItemAsistencia[] = Object.entries(marcas).map(
      ([alumno_id, estado]) => ({
        alumno_id,
        estado,
      })
    );

    try {
      const res = await validarLoteAsistencia(
        profesor.id,
        comision.id,
        claseSeleccionadaId,
        registros
      );
      setResultadoValidacion(res);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Error al validar la asistencia en el servidor');
      }
    } finally {
      setValidando(false);
    }
  };

  return (
    <div className="tab-card-content">
      <div className="panel-intro-header">
        <div>
          <div className="section-category">Funcionalidades F3 / F4</div>
          <h3 className="panel-title">
            Toma de Asistencia Áulica — Comisión {comision.codigo}
          </h3>
          <p className="panel-subtitle">
            Control de asistencia presencial rápido y táctil. Estados mutuamente excluyentes (R-ASI-01) con soporte para tomas parciales (R-ASI-02).
          </p>
        </div>

        {(cargandoClases || cargandoNomina) && (
          <div className="loading-badge" role="status">
            <span className="spinner" aria-hidden="true" /> Sincronizando...
          </div>
        )}
      </div>

      {error && (
        <div className="alert alert-error" role="alert">
          <strong>Atención:</strong> {error}
        </div>
      )}

      {/* Selector de Sesión de Clase */}
      <div className="session-selector-card">
        <div className="session-selector-top">
          <div className="session-label-group">
            <span className="session-icon" aria-hidden="true">📅</span>
            <div>
              <label htmlFor="select-instancia-clase" className="session-title-label">
                Sesión de Clase Seleccionada:
              </label>
              <p className="session-help-text">
                Una comisión puede dictar múltiples clases en la misma fecha (R-CLS-01).
              </p>
            </div>
          </div>

          <button
            type="button"
            className="btn btn-sm btn-outline"
            onClick={() => setMostrarNuevaClase(!mostrarNuevaClase)}
            aria-expanded={mostrarNuevaClase}
          >
            {mostrarNuevaClase ? '✕ Cancelar' : '+ Nueva Clase / Sesión'}
          </button>
        </div>

        {mostrarNuevaClase ? (
          <form onSubmit={handleCrearClase} className="session-create-form" aria-label="Nueva sesión">
            <div className="form-grid-row">
              <div className="form-field">
                <label htmlFor="new-class-date" className="field-label">Fecha de Cursada *</label>
                <input
                  id="new-class-date"
                  type="date"
                  className="input-text"
                  value={nuevaFecha}
                  onChange={(e) => setNuevaFecha(e.target.value)}
                  required
                />
              </div>

              <div className="form-field flex-1">
                <label htmlFor="new-class-desc" className="field-label">Tema o Descripción Pedagógica</label>
                <input
                  id="new-class-desc"
                  type="text"
                  className="input-text"
                  placeholder="Ej: Módulo 3 — Taller práctico de arquitectura"
                  value={nuevaDescripcion}
                  onChange={(e) => setNuevaDescripcion(e.target.value)}
                />
              </div>
            </div>

            <div className="session-form-actions">
              <button
                type="submit"
                className="btn btn-primary"
                disabled={creandoClase}
              >
                {creandoClase ? 'Creando clase...' : 'Crear e Iniciar Toma'}
              </button>
            </div>
          </form>
        ) : (
          <div className="session-dropdown-area">
            {clases.length === 0 ? (
              <div className="session-empty-hint">
                <span>No hay clases registradas para esta comisión.</span>
                <button
                  type="button"
                  className="btn-link-action"
                  onClick={() => setMostrarNuevaClase(true)}
                >
                  Registrar la primera clase
                </button>
              </div>
            ) : (
              <div className="session-select-wrapper">
                <select
                  id="select-instancia-clase"
                  className="input-select session-select"
                  value={claseSeleccionadaId}
                  onChange={(e) => {
                    setClaseSeleccionadaId(e.target.value);
                    setResultadoValidacion(null);
                  }}
                >
                  {clases.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.fecha} — {c.descripcion_opcional || 'Clase ordinaria'}
                    </option>
                  ))}
                </select>
                <span className="session-audited-tag">
                  Docente registrador: {profesor.nombre_completo}
                </span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Ribbon de Métricas en Vivo */}
      <div className="attendance-metrics-dashboard" role="region" aria-label="Resumen de asistencia">
        <div className="metric-box metric-box-total">
          <span className="metric-count">{totalAlumnos}</span>
          <span className="metric-text">Total Nómina</span>
        </div>
        <div className="metric-box metric-box-present">
          <span className="metric-count">{presentesCount}</span>
          <span className="metric-text">Presentes</span>
        </div>
        <div className="metric-box metric-box-absent">
          <span className="metric-count">{ausentesCount}</span>
          <span className="metric-text">Ausentes</span>
        </div>
        <div className="metric-box metric-box-late">
          <span className="metric-count">{tardesCount}</span>
          <span className="metric-text">Tardes</span>
        </div>
        <div className="metric-box metric-box-unmarked">
          <span className="metric-count">{sinMarcarCount}</span>
          <span className="metric-text">Sin Marcar</span>
        </div>

        <div className="quick-attendance-toolbar">
          <button
            type="button"
            className="btn btn-sm btn-secondary"
            onClick={handleMarcarTodosPresentes}
            disabled={totalAlumnos === 0}
            title="Asigna 'Presente' a toda la nómina de cursada"
          >
            ✓ Todos Presentes
          </button>
          <button
            type="button"
            className="btn btn-sm btn-ghost"
            onClick={handleLimpiarMarcas}
            disabled={marcadosCount === 0}
          >
            ↺ Limpiar
          </button>
        </div>
      </div>

      {/* Grilla Áulica Táctil para Cada Alumno */}
      {nomina.length === 0 ? (
        <div className="empty-state-box" role="status">
          <div className="empty-icon" aria-hidden="true">👥</div>
          <h4 className="empty-title">Sin alumnos activos</h4>
          <p className="empty-desc">
            No se registran alumnos con inscripción activa en esta comisión.
          </p>
        </div>
      ) : (
        <div
          className="attendance-sheet-grid"
          role="list"
          aria-label="Lista de alumnos para marcar asistencia"
        >
          {nomina.map((vinculo) => {
            const alumno = vinculo.alumno;
            const estadoActual = marcas[alumno.id];
            const iniciales = alumno.nombre_completo
              .split(' ')
              .map((n) => n[0])
              .slice(0, 2)
              .join('')
              .toUpperCase();

            return (
              <div
                key={alumno.id}
                role="listitem"
                className={`attendance-student-row ${estadoActual ? `row-state-${estadoActual.toLowerCase()}` : ''}`}
              >
                <div className="student-card-info">
                  <div className="student-avatar" aria-hidden="true">
                    {iniciales}
                  </div>
                  <div className="student-details">
                    <span className="student-name">{alumno.nombre_completo}</span>
                    <span className="student-id-code">
                      Legajo: <strong>{alumno.identificador_academico}</strong>
                    </span>
                  </div>
                </div>

                {/* Botones Segmentados Táctiles de al menos 44px */}
                <div
                  className="attendance-button-group"
                  role="group"
                  aria-label={`Asistencia para ${alumno.nombre_completo}`}
                >
                  <button
                    type="button"
                    className={`btn-state btn-state-p ${estadoActual === 'PRESENTE' ? 'btn-state-active' : ''}`}
                    onClick={() => handleMarcar(alumno.id, 'PRESENTE')}
                    aria-pressed={estadoActual === 'PRESENTE'}
                    aria-label={`Marcar Presente a ${alumno.nombre_completo}`}
                  >
                    <span className="state-letter" aria-hidden="true">P</span>
                    <span className="state-label">Presente</span>
                  </button>

                  <button
                    type="button"
                    className={`btn-state btn-state-a ${estadoActual === 'AUSENTE' ? 'btn-state-active' : ''}`}
                    onClick={() => handleMarcar(alumno.id, 'AUSENTE')}
                    aria-pressed={estadoActual === 'AUSENTE'}
                    aria-label={`Marcar Ausente a ${alumno.nombre_completo}`}
                  >
                    <span className="state-letter" aria-hidden="true">A</span>
                    <span className="state-label">Ausente</span>
                  </button>

                  <button
                    type="button"
                    className={`btn-state btn-state-t ${estadoActual === 'TARDE' ? 'btn-state-active' : ''}`}
                    onClick={() => handleMarcar(alumno.id, 'TARDE')}
                    aria-pressed={estadoActual === 'TARDE'}
                    aria-label={`Marcar Tarde a ${alumno.nombre_completo}`}
                  >
                    <span className="state-letter" aria-hidden="true">T</span>
                    <span className="state-label">Tarde</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Botón de Validación de Lote */}
      <div className="attendance-action-footer">
        <button
          type="button"
          className="btn btn-primary btn-lg"
          onClick={handleValidarAsistencia}
          disabled={validando || !claseSeleccionadaId || marcadosCount === 0}
        >
          {validando ? 'Validando en Servidor...' : 'Validar Lote de Asistencia en Servidor'}
        </button>
        <p className="validation-footer-hint">
          Comprueba reglas pedagógicas en el servidor (R-ASI-01 a R-ASI-04) y el alcance docente Zero Trust.
        </p>
      </div>

      {/* Resultado de Validación y Banner DEC-017 */}
      {resultadoValidacion && (
        <div
          className={`validation-result-card ${resultadoValidacion.valido ? 'result-success' : 'result-failure'}`}
          role="region"
          aria-labelledby="validation-result-title"
        >
          <div className="result-card-header">
            <h4 id="validation-result-title" className="result-title">
              {resultadoValidacion.valido
                ? '✓ Lote de Asistencia Validado por el Servidor'
                : '✕ Inconsistencia Detectada en el Servidor'}
            </h4>
            <span className="badge-class-date">
              Fecha de la Clase: {resultadoValidacion.fecha_clase}
            </span>
          </div>

          <p className="result-message-text">{resultadoValidacion.mensaje}</p>

          <div className="result-breakdown-strip">
            <div className="breakdown-item">Nómina: <strong>{resultadoValidacion.resumen.total_nomina}</strong></div>
            <div className="breakdown-item">Marcados: <strong>{resultadoValidacion.resumen.marcados}</strong></div>
            <div className="breakdown-item text-success">Presentes: <strong>{resultadoValidacion.resumen.presentes}</strong></div>
            <div className="breakdown-item text-danger">Ausentes: <strong>{resultadoValidacion.resumen.ausentes}</strong></div>
            <div className="breakdown-item text-warning">Tardes: <strong>{resultadoValidacion.resumen.tardes}</strong></div>
            <div className="breakdown-item text-muted">Sin marcar: <strong>{resultadoValidacion.resumen.sin_marcar}</strong></div>
          </div>

          {resultadoValidacion.es_toma_parcial && (
            <div className="alert-inline alert-info">
              ℹ <strong>Toma Parcial Habilitada (R-ASI-02):</strong> El lote no comprende a la totalidad de la nómina. Esta modalidad es válida en la cursada.
            </div>
          )}

          {/* Banner Institucional DEC-017 */}
          <div className="dec017-institutional-banner" role="note">
            <div className="dec017-header">
              <span className="dec017-badge">Aviso Institucional (DEC-017)</span>
              <span className="dec017-status-tag">Estado: {resultadoValidacion.estado_persistencia}</span>
            </div>
            <p className="dec017-explanation">
              La verificación técnica del dominio pedagógico ha concluido favorablemente. No obstante, la <em>propiedad de la persistencia definitiva</em> se encuentra actualmente en evaluación institucional (Escenario A: custodia directa en el SGA vs. Escenario B: delegación en el Sistema Central). Por tal motivo, los datos <strong>no son declarados como almacenados de forma permanente</strong> en la base institucional oficial.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
