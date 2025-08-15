# 🚀 Jarvis Hybrid-Ready Quickstart

## Snabb Ready-to-Run (hybrid)

### 1) Start
```bash
# Komplett setup
make hybrid-setup

# Eller steg för steg:
make install-prod
make types
```

### 2) Verifiera kontrakt & SLA
```bash
# Kör alla verifieringar
make verify-harden

# Eller individuellt:
make verify          # Go/No-Go runner
make selftest        # Core selftest
make report-slowest  # Performance rapport
```

### 3) (Valfritt) TLS lokalt
```bash
make tls-setup       # Skapa certifikat
ENABLE_TLS=true make tls-dev  # Starta med TLS
```

### 4) UI smoke (läggs i CI också)
```bash
cd ui && npx playwright test
```

## 🌟 Nya Hybrid-Features

### API-nyckel & Secrets
- **Multi-key support**: `API_KEYS=key1,key2,key3`
- **Rotation-ready**: Enkelt att byta nycklar
- **Prod-secrets**: Dokumenterat för 1Password/Keychain

### Next.js + CSP (strikt men dev-vänlig)
- **Middleware**: Automatisk CSP-headers
- **Dev-friendly**: Tillåter localhost för utveckling
- **Security**: XSS, CSRF, Clickjacking protection

### SSE via Next dev proxy (stabil reconnect)
- **Proxy**: `/_core/*` → `http://127.0.0.1:8000/*`
- **CORS-free**: Ingen CORS-konfiguration behövs
- **Reconnect**: Automatisk återanslutning vid fel

### OpenAPI → TS typer (säkerställd drift)
- **Auto-generate**: `make types`
- **Contract check**: `make types-check` (CI-gate)
- **Version sync**: Typer uppdateras automatiskt

### UI smoke-tester (Playwright)
- **E2E testing**: Översikt, loggar, verktyg
- **Error handling**: Core offline, SSE-fel, empty states
- **Accessibility**: ARIA-labels, keyboard navigation

### Desktop-bro (förberett)
- **Tauri setup**: Komplett desktop-app struktur
- **Autostart**: macOS launchd, Windows Task Scheduler, Linux systemd
- **Health gate**: Vägrar starta om Core ej nås

### Graceful shutdown & port-probe
- **Port conflict**: Tydlig felmeddelande vid EADDRINUSE
- **Clean shutdown**: Stänger SSE-clients, flushar JSONL
- **Exit codes**: Korrekt exit-koder för CI/CD

## 🔧 Konfiguration

### Environment Variables
```bash
# Core
API_KEYS=dev-key-1,dev-key-2
LOG_BUFFER_MAX=1000
LOG_BUFFER_POLICY=drop_oldest

# UI
NEXT_PUBLIC_CORE_BASE_URL=http://127.0.0.1:8000
NEXT_PUBLIC_ENABLE_SSE=true

# Desktop
CORE_BASE_URL=http://127.0.0.1:8000
API_KEY=dev-key-1
```

### Makefile Targets
```bash
# Hybrid setup
make hybrid-setup      # Komplett setup
make hybrid-dev        # Starta utvecklingsmiljö

# Verifiering
make verify            # Go/No-Go runner
make verify-harden     # Selftest + verify
make types-check       # Kontrollera API-kontrakt

# Testing
make test-ui           # UI Playwright tester
make report-slowest    # Performance rapport

# TLS
make tls-setup         # Skapa certifikat
make tls-dev           # Starta med TLS
```

## 🧪 Testing Strategy

### Core Testing
- **Unit tests**: Pytest för alla komponenter
- **Integration**: API endpoints, middleware
- **Performance**: p50/p95/p99 SLA-validering
- **Security**: API key, CORS, rate limiting

### UI Testing
- **Component tests**: React komponenter
- **E2E tests**: Playwright för användarflöden
- **Accessibility**: ARIA, keyboard navigation
- **Error handling**: Offline states, error boundaries

### Hybrid Testing
- **Contract validation**: OpenAPI → TS types
- **Cross-layer**: Core ↔ UI kommunikation
- **Performance**: End-to-end latens
- **Security**: CSP, headers, authentication

## 🚀 Deployment

### Development
```bash
# Terminal 1: Core API
cd core && make dev

# Terminal 2: UI Dashboard
cd ui && npm run dev

# Terminal 3: Desktop App (valfritt)
cd desktop && npm run tauri dev
```

### Production
```bash
# Core
cd core && make install-prod
make tls-setup  # Om HTTPS behövs
ENABLE_TLS=true make tls-dev

# UI
cd ui && npm run build
npm run start

# Desktop
cd desktop && npm run tauri build
```

### CI/CD
```bash
# GitHub Actions
- Install dependencies
- Run tests (Core + UI)
- Build artifacts
- Deploy to staging/production
```

## 🔒 Säkerhet

### API Security
- **Multi-key rotation**: Enkelt att byta nycklar
- **Rate limiting**: GET 10 rps, POST 2 rps
- **CORS**: Strikt konfiguration för produktion
- **TLS**: Lokal HTTPS med mkcert

### UI Security
- **CSP**: Content Security Policy
- **Headers**: XSS, CSRF, Clickjacking protection
- **Proxy**: Lokal API-kommunikation
- **Error boundaries**: Säker felhantering

### Desktop Security
- **Sandbox**: Tauri sandbox
- **Local only**: Endast lokala anslutningar
- **Health gate**: Validering innan start
- **Autostart**: Säker system-integration

## 📊 Monitoring

### Metrics
- **Router performance**: Hit rate, latens
- **End-to-end**: Total request time
- **Error rates**: Per endpoint, per error type
- **Resource usage**: CPU, memory, disk

### Logging
- **JSONL format**: Strukturerad loggning
- **PII masking**: Automatisk maskning
- **Correlation IDs**: Request tracking
- **Ring buffer**: In-memory med backpressure

### Health Checks
- **Liveness**: `/health/live`
- **Readiness**: `/health/ready`
- **Startup**: Port availability, dependencies
- **Shutdown**: Graceful cleanup

## 🆘 Troubleshooting

### Vanliga Problem
1. **Port conflict**: Använd `make tls-dev` eller ändra port
2. **API key**: Kontrollera `API_KEYS` i `.env`
3. **CORS**: Använd `/_core/*` proxy i UI
4. **TLS**: Kör `make tls-setup` för lokala certifikat

### Debug
```bash
# Core logs
tail -f core/logs/jarvis-core.log

# UI logs
cd ui && npm run dev

# Performance
make report-slowest

# Health check
curl http://127.0.0.1:8000/health/live
```

---

**Nu är du redo för hybrid-deployment!** ✨

För support, se `docs/adr/0001-hybrid-architecture.md` eller skapa issue i projektet.
