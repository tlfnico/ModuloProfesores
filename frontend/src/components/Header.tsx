import type { Profesor } from '../types';

interface HeaderProps {
  profesor?: Profesor | null;
}

export function Header({ profesor }: HeaderProps) {
  // Iniciales para el avatar del docente
  const iniciales = profesor
    ? profesor.nombre_completo
        .split(' ')
        .map((n) => n[0])
        .slice(0, 2)
        .join('')
        .toUpperCase()
    : 'DOC';

  return (
    <header className="app-header" role="banner">
      <div className="container header-container">
        <div className="header-brand">
          <div className="header-logo-icon" aria-hidden="true">
            <svg
              width="28"
              height="28"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
              <path d="M6 12v5c3 3 9 3 12 0v-5" />
            </svg>
          </div>
          <div>
            <div className="header-institution-tag">
              Sistema de Gestión Académica
            </div>
            <h1 className="header-title">Módulo Profesor</h1>
          </div>
        </div>

        {profesor && (
          <div className="header-user-profile" aria-label="Perfil del docente activo">
            <div className="user-avatar" aria-hidden="true">
              {iniciales}
            </div>
            <div className="user-info">
              <span className="user-name">{profesor.nombre_completo}</span>
              <span className="user-legajo">Legajo: {profesor.identificador_laboral}</span>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
