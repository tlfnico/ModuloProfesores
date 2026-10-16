import { Header } from './components/Header';
import { StatusCard } from './components/StatusCard';
import './index.css';

export function App() {
  return (
    <>
      <a href="#main-content" className="skip-link">
        Saltar al contenido principal
      </a>

      <Header />

      <main id="main-content" className="container main-content" tabIndex={-1}>
        <section className="card card-intro" aria-labelledby="intro-title">
          <h2 id="intro-title" className="card-title">
            Inicialización Técnica del Entorno
          </h2>
          <p className="card-description">
            Base técnica inicial del <strong>Módulo Profesor</strong> del Sistema de
            Gestión Académica (SGA). La estructura está preparada con separación
            limpia de responsabilidades y compatibilidad de accesibilidad (WCAG 2.1 AA).
          </p>

          <div className="status-grid">
            <div className="status-item">
              <span className="status-label">Backend</span>
              <span className="status-value">Django REST Framework + drf-spectacular</span>
            </div>
            <div className="status-item">
              <span className="status-label">Frontend</span>
              <span className="status-value">React 19 + TypeScript (Vite)</span>
            </div>
            <div className="status-item">
              <span className="status-label">Base de Datos</span>
              <span className="status-value">PostgreSQL 18</span>
            </div>
            <div className="status-item">
              <span className="status-label">Cuestión Abierta</span>
              <span className="status-value">DEC-017: Propiedad de Persistencia de Asistencia</span>
            </div>
          </div>
        </section>

        <StatusCard />

        <section className="card" aria-labelledby="scope-title">
          <h2 id="scope-title" className="card-title">
            Próximos Pasos (Bloque 2)
          </h2>
          <p className="card-description">
            Una vez validado el arranque y la estructura técnica de este Bloque 1,
            se comenzará el desarrollo incremental del MVP:
          </p>
          <ul className="step-list">
            <li><strong>F1 — Consulta de comisiones asignadas:</strong> acceso docente por período lectivo.</li>
            <li><strong>F2 — Consulta de nómina de alumnos:</strong> visualización de estudiantes matriculados.</li>
            <li><strong>F3 — Registro de asistencia áulica:</strong> toma rápida con soporte para estados presente, ausente y tarde.</li>
            <li><strong>F4 — Historial de asistencias:</strong> consulta de registros previos y porcentajes.</li>
            <li><strong>F5 — Registro de observaciones:</strong> notas pedagógicas por alumno y comisión.</li>
            <li><strong>F6 — Auditoría y seguridad:</strong> validación estricta de alcance docente (Zero Trust).</li>
          </ul>
        </section>
      </main>

      <footer className="app-footer" role="contentinfo">
        <div className="container footer-content">
          <p>
            Sistema de Gestión Académica — Tecnicatura Superior en Desarrollo de Software.
          </p>
          <p className="footer-note">
            Diseñado con prioridad de accesibilidad, baja carga cognitiva y diseño responsivo.
          </p>
        </div>
      </footer>
    </>
  );
}

export default App;
