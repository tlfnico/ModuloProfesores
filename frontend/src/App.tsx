import { useState } from 'react';
import { AsistenciaAulica } from './components/AsistenciaAulica';
import { ComisionesList } from './components/ComisionesList';
import { Header } from './components/Header';
import { NominaTable } from './components/NominaTable';
import { ObservacionesPanel } from './components/ObservacionesPanel';
import { ProfesorSelector } from './components/ProfesorSelector';
import { StatusCard } from './components/StatusCard';
import type { Comision, Profesor } from './types';
import './index.css';

type TabId = 'nomina' | 'asistencia' | 'observaciones';

export function App() {
  const [profesor, setProfesor] = useState<Profesor | null>(null);
  const [comision, setComision] = useState<Comision | null>(null);
  const [tabActiva, setTabActiva] = useState<TabId>('nomina');
  const [alumnoParaObservacionId, setAlumnoParaObservacionId] = useState<string | null>(null);
  const [mostrarDiagnostico, setMostrarDiagnostico] = useState(false);

  const handleSeleccionarProfesor = (nuevoProfesor: Profesor) => {
    setProfesor(nuevoProfesor);
    setComision(null);
    setAlumnoParaObservacionId(null);
  };

  const handleSeleccionarComision = (nuevaComision: Comision) => {
    setComision(nuevaComision);
    setAlumnoParaObservacionId(null);
  };

  const handleIrAObservacionAlumno = (alumnoId: string) => {
    setAlumnoParaObservacionId(alumnoId);
    setTabActiva('observaciones');
  };

  return (
    <div className="app-layout-wrapper">
      <a href="#main-content" className="skip-link">
        Saltar al contenido principal
      </a>

      {/* Header Institucional Superior */}
      <Header profesor={profesor} />

      <main id="main-content" className="container app-main-content" tabIndex={-1}>
        {/* Barra de Identidad de Desarrollo (Scope Zero Trust) */}
        <ProfesorSelector
          profesorSeleccionado={profesor}
          onSeleccionarProfesor={handleSeleccionarProfesor}
        />

        {profesor && (
          <>
            {/* F1: Comisiones Asignadas */}
            <ComisionesList
              profesor={profesor}
              comisionSeleccionada={comision}
              onSeleccionarComision={handleSeleccionarComision}
            />

            {/* Espacio Operativo de la Comisión Seleccionada */}
            {comision ? (
              <section
                className="commission-workspace-card"
                aria-label={`Espacio de gestión de la Comisión ${comision.codigo}`}
              >
                {/* Cabecera Contextual de la Comisión */}
                <div className="workspace-header-banner">
                  <div className="workspace-header-main">
                    <div className="workspace-tag-row">
                      <span className="badge-active-commission">
                        Comisión Seleccionada
                      </span>
                      <span className="badge-period-name">
                        {comision.periodo_lectivo.nombre}
                      </span>
                    </div>

                    <h2 className="workspace-commission-title">
                      {comision.descripcion || `Comisión ${comision.codigo}`}
                    </h2>

                    <div className="workspace-subjects-summary">
                      <span className="subjects-label">Materias de la cursada:</span>
                      <div className="subjects-inline-list">
                        {comision.materias.map((m) => (
                          <span key={m.id} className="subject-chip-simple">
                            {m.nombre} <code>({m.codigo})</code>
                          </span>
                        ))}
                        {comision.materias.length === 0 && (
                          <span className="text-muted-italic">Sin materias asignadas</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Navegación por Pestañas (Tablist Accesible WCAG 2.1 AA) */}
                <div
                  className="modern-tabs-nav"
                  role="tablist"
                  aria-label="Operaciones de cursada de la comisión"
                >
                  <button
                    id="tab-nomina"
                    type="button"
                    role="tab"
                    aria-selected={tabActiva === 'nomina'}
                    aria-controls="panel-nomina"
                    className={`tab-item-btn ${tabActiva === 'nomina' ? 'tab-item-active' : ''}`}
                    onClick={() => setTabActiva('nomina')}
                  >
                    <span className="tab-item-icon" aria-hidden="true">👥</span>
                    <span className="tab-item-text">Nómina de Estudiantes</span>
                  </button>

                  <button
                    id="tab-asistencia"
                    type="button"
                    role="tab"
                    aria-selected={tabActiva === 'asistencia'}
                    aria-controls="panel-asistencia"
                    className={`tab-item-btn ${tabActiva === 'asistencia' ? 'tab-item-active' : ''}`}
                    onClick={() => setTabActiva('asistencia')}
                  >
                    <span className="tab-item-icon" aria-hidden="true">📋</span>
                    <span className="tab-item-text">Asistencia Áulica</span>
                  </button>

                  <button
                    id="tab-observaciones"
                    type="button"
                    role="tab"
                    aria-selected={tabActiva === 'observaciones'}
                    aria-controls="panel-observaciones"
                    className={`tab-item-btn ${tabActiva === 'observaciones' ? 'tab-item-active' : ''}`}
                    onClick={() => setTabActiva('observaciones')}
                  >
                    <span className="tab-item-icon" aria-hidden="true">📝</span>
                    <span className="tab-item-text">Observaciones Académicas</span>
                  </button>
                </div>

                {/* Paneles de Contenido */}
                <div className="tab-viewport">
                  {tabActiva === 'nomina' && (
                    <div
                      id="panel-nomina"
                      role="tabpanel"
                      aria-labelledby="tab-nomina"
                    >
                      <NominaTable
                        profesor={profesor}
                        comision={comision}
                        onSeleccionarAlumnoParaObservacion={handleIrAObservacionAlumno}
                      />
                    </div>
                  )}

                  {tabActiva === 'asistencia' && (
                    <div
                      id="panel-asistencia"
                      role="tabpanel"
                      aria-labelledby="tab-asistencia"
                    >
                      <AsistenciaAulica
                        profesor={profesor}
                        comision={comision}
                      />
                    </div>
                  )}

                  {tabActiva === 'observaciones' && (
                    <div
                      id="panel-observaciones"
                      role="tabpanel"
                      aria-labelledby="tab-observaciones"
                    >
                      <ObservacionesPanel
                        profesor={profesor}
                        comision={comision}
                        alumnoPreseleccionadoId={alumnoParaObservacionId}
                      />
                    </div>
                  )}
                </div>
              </section>
            ) : (
              <div className="empty-state-box" role="status">
                <div className="empty-icon" aria-hidden="true">📂</div>
                <h3 className="empty-title">Seleccioná una comisión</h3>
                <p className="empty-desc">
                  Elegí una de las comisiones del período para consultar la nómina de estudiantes, registrar asistencias y notas formativas.
                </p>
              </div>
            )}
          </>
        )}

        {/* Diagnóstico Técnico y Estado DEC-017 */}
        <section className="diagnostico-collapsible-section" aria-labelledby="diag-heading">
          <div className="diagnostico-collapsible-header">
            <div>
              <h3 id="diag-heading" className="diagnostico-section-title">
                Diagnóstico del Entorno y Estado Técnico
              </h3>
              <p className="diagnostico-section-subtitle">
                Conexión con Django REST Framework y verificación de DEC-017.
              </p>
            </div>
            <button
              type="button"
              className="btn btn-sm btn-outline"
              onClick={() => setMostrarDiagnostico(!mostrarDiagnostico)}
              aria-expanded={mostrarDiagnostico}
            >
              {mostrarDiagnostico ? 'Ocultar Diagnóstico' : 'Ver Diagnóstico Técnico'}
            </button>
          </div>

          {mostrarDiagnostico && (
            <div className="diagnostico-details-box">
              <StatusCard />
            </div>
          )}
        </section>
      </main>

      {/* Footer Institucional */}
      <footer className="app-footer" role="contentinfo">
        <div className="container footer-inner">
          <div className="footer-credits">
            <strong>Sistema de Gestión Académica (SGA)</strong> — Tecnicatura Superior en Desarrollo de Software.
          </div>
          <div className="footer-compliance">
            Módulo Profesor — Cumplimiento WCAG 2.1 AA | Usabilidad Áulica Responsiva.
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
