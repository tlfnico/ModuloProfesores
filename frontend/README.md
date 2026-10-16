# Frontend — Sistema Profesor (SGA)

## 1. Estado Actual
**Base técnica inicial configurada y verificada (Bloque 1).**  
La aplicación cliente está construida sobre React 19 con TypeScript mediante Vite. Dispone de configuración de variables de entorno (`.env.example`), diseño centrado en accesibilidad (WCAG 2.1 AA), cliente de comprobación de salud del backend y compilación validada con `tsc` y `oxlint`.

---

## 2. Estructura de Directorios

```text
frontend/
├── .env.example              # Variables de entorno para Vite (VITE_API_URL)
├── package.json              # Dependencias y scripts de desarrollo
├── tsconfig.json             # Configuración de TypeScript
├── vite.config.ts            # Configuración de compilador y servidor Vite
├── index.html                # Plantilla HTML raíz con metadatos y lang="es"
└── src/
    ├── api/                  # Cliente HTTP para comunicación con el backend
    │   └── client.ts         # Funciones de consulta a la API REST (checkBackendHealth)
    ├── components/           # Componentes UI reutilizables y accesibles
    │   ├── Header.tsx        # Encabezado semántico institucional
    │   └── StatusCard.tsx    # Tarjeta de diagnóstico de estado con soporte ARIA
    ├── types/                # Interfaces y tipos TypeScript
    │   └── index.ts          # Tipos de respuesta de salud y errores
    ├── App.tsx               # Vista principal de inicialización y diagnóstico
    ├── index.css             # Sistema de estilos accesible (WCAG 2.1 AA, mobile-first)
    └── main.tsx              # Punto de entrada de renderizado React
```

---

## 3. Comandos de Instalación, Ejecución y Calidad

### 3.1. Instalación de Dependencias
```powershell
# En el directorio frontend/
npm install
```

### 3.2. Configuración de Variables de Entorno
Copiar el archivo de plantilla:
```powershell
Copy-Item .env.example .env
```
Por defecto, `VITE_API_URL` apunta a `http://localhost:8000/api`.

### 3.3. Servidor de Desarrollo
```powershell
npm run dev
```
La aplicación estará accesible en el navegador (por defecto `http://localhost:5173`).

### 3.4. Compilación y Calidad de Código
```powershell
# Compilación estricta de TypeScript y bundle de producción
npm run build

# Análisis estático y linter con oxlint
npm run lint
```

---

## 4. Principios de Accesibilidad y Usabilidad Implementados
- **Navegación por teclado y foco visible:** Anillo de foco de alto contraste (`3px solid #025091` con `outline-offset`) y enlace visible de salto al contenido principal (*Skip Link*).
- **Semántica HTML y ARIA:** Estructura con `<header>`, `<main>`, `<section>`, `<footer>` y regiones dinámicas con `role="region" aria-live="polite"`.
- **Contraste de color óptimo:** Relación de contraste superior a 4.5:1 para todo el texto.
- **Mobile-first y áreas táctiles:** Botones y controles con área mínima interactiva de 44x44 px adaptados para uso áulico en dispositivos táctiles.
