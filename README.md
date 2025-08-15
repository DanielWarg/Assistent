# Jarvis (Hybrid Solution)

En lokal AI-assistent med edge-first bearbetning och omfattande observability.

## 🏗️ Arkitektur

### Core (`/core`)
- **FastAPI-baserad backend** med router-first approach
- **Lokal LLM-integration** via Ollama
- **Verktygsintegrationer** (Spotify, kalender, mail, etc.)
- **Omfattande observability** med JSONL-loggning och metrics
- **Python 3.11+** med moderna type hints och Pydantic v2

### Dashboard UI (`/ui`)
- **Next.js 14 dashboard** för övervakning och konfiguration
- **Realtids-loggvisning** via Server-Sent Events (SSE)
- **Prestandamätning** och trendanalys
- **Selftest-körning** och resultatvisning
- **Tailwind CSS** med shadcn/ui-komponenter

### Desktop App (`/desktop`)
- **SwiftUI-baserad menyradsapp** (kommer senare)
- **Snabbåtkomst** till vanliga kommandon
- **Mikrofonstyrning** och notifieringar

## 🚀 Snabbstart

### Förutsättningar
- Python 3.11+
- Node.js 18+
- Docker (valfritt)

### Installation
```bash
# Klona repot
git clone <repo-url>
cd jarvis

# Komplett setup
make setup

# Eller manuellt:
cd core && python3.11 -m venv .venv
cd core && source .venv/bin/activate && make install
cd ui && npm install

# Alternativt med requirements.txt:
cd core && python3.11 -m venv .venv
cd core && source .venv/bin/activate && make install-prod  # endast production
cd core && source .venv/bin/activate && make install-dev   # development + production
```

### Utveckling
```bash
# Starta både Core och UI
make dev

# Eller separat:
make dev-core    # Endast Core (port 8000)
make dev-ui      # Endast UI (port 3000)
```

### Tester
```bash
# Kör alla tester
make test

# Eller separat:
make test-core   # Core tester
make test-ui     # UI tester
```

### 🚀 Go/No-Go Test (Hybrid Readiness)

För att verifiera att Jarvis Core är redo för hybrid-deployment:

```bash
# Snabb test
cd core
./quick_test.sh

# Go/No-Go runner (rekommenderat)
make verify

# Full verify & harden
make verify-harden

# Legacy Go/No-Go test
make go-no-go

# Root level
make verify  # från root
```

**Go/No-Go kriterier:**
- ✅ **GO**: Alla tester passerar, p95 inom SLA, SSE stabil
- ❌ **NO-GO**: Något test misslyckas, p95 över SLA, SSE kraschar

**Go/No-Go Runner Features:**
- **Automatisk SLA-validering** (p95 ≤ 500ms)
- **SSE stabilitetstest** (2 parallella läsare, 200 requests)
- **API-nyckel autentisering** (401/403/200 validering)
- **OpenAPI kontrakt** verifiering
- **JSON + Markdown rapporter** i `./logs/`
- **Exit code 1** om något bryter SLA/krav

### 🔐 TLS Setup (Hybrid Development)

För säker kommunikation mellan Core och UI:

```bash
# Skapa TLS-certifikat (kräver mkcert)
make tls-setup

# Starta Core med TLS
make tls-dev

# Eller från root
make tls-setup  # skapa certifikat
make tls-dev    # starta med TLS
```

**Installera mkcert:**
```bash
# macOS
brew install mkcert nss

# Ubuntu/Debian
sudo apt install mkcert

# Windows
choco install mkcert
```

## 📊 API Endpoints

### Core API (port 8000)
- `GET /` - Root endpoint
- `GET /health/live` - Health check
- `GET /health/ready` - Readiness check
- `GET /info` - Applikationsinfo
- `GET /metrics/*` - Metrics och prestanda
- `GET /logs/*` - Loggning och SSE-streaming
- `GET /router/*` - Router API
- `GET /tools/*` - Tools API

### UI Dashboard (port 3000)
- `/` - Huvudsida med översikt
- `/overview` - Systemstatus och metrics
- `/logs` - Realtids-loggvisning
- `/selftest` - Diagnostik och health checks

## 🛠️ Utvecklingsverktyg

### Core
- **FastAPI** med Pydantic v2
- **Uvicorn** med hot reload
- **Pytest** med code coverage
- **Black** och **Ruff** för kodformatering
- **MyPy** för type checking
- **Pre-commit hooks** för kodkvalitet

### UI
- **Next.js 14** med App Router
- **TypeScript** med strikt type checking
- **Tailwind CSS** för styling
- **Zustand** för state management
- **Recharts** för datavisualisering

### DevOps
- **Docker** med multi-stage builds
- **Docker Compose** för lokal utveckling
- **GitHub Actions** för CI/CD
- **Security scanning** med Bandit och Safety

## 📈 Observability

### Loggning
- **Strukturerad loggning** i JSONL-format
- **Realtids-streaming** via SSE
- **PII-masking** för säkerhet
- **Correlation-ID** för request tracking
- **Log rotation** och retention policies

### Metrics
- **Router performance** (p50/p95/p99 latency)
- **End-to-end metrics** för hela flödet
- **Error rates** och typologi
- **System resources** (CPU, minne, disk)
- **Prometheus/Grafana** integration (förberedd)

### Monitoring
- **Health checks** med custom probes
- **Performance tracking** med timing middleware
- **Error handling** med global exception handler
- **Request correlation** för debugging

## 🔒 Säkerhet

### Autentisering & Auktorisering
- **API key authentication** (konfigurerad)
- **JWT tokens** (förberedd)
- **Role-based access control** (förberedd)

### Säkerhetsåtgärder
- **CORS-konfiguration** med whitelist
- **TrustedHost middleware** för production
- **Input validation** med Pydantic
- **SQL injection protection** via SQLAlchemy
- **XSS protection** med proper headers

### Compliance
- **GDPR-ready** med PII-masking
- **Audit logging** för säkerhetshändelser
- **Data retention** policies

## 🧪 Testing Strategy

### Testnivåer
- **Unit tests** med pytest
- **Integration tests** för API endpoints
- **End-to-end tests** med flow_selftest
- **Performance tests** med p50/p95 SLA

### Testverktyg
- **Pytest** med fixtures och parametrization
- **Coverage reporting** med HTML/XML output
- **Test markers** för kategorisering
- **Mocking** med unittest.mock

### CI/CD Pipeline
- **Automated testing** på alla commits
- **Security scanning** med Bandit och Safety
- **Code quality** med linting och formatting
- **Docker builds** med caching

## 📁 Projektstruktur

```
jarvis/
├── core/                          # FastAPI backend
│   ├── src/
│   │   ├── app/                   # Main application
│   │   ├── observability/         # Metrics, logs, monitoring
│   │   ├── router/                # Router logic
│   │   ├── tools/                 # Tool integrations
│   │   ├── llm/                   # LLM integration
│   │   ├── proactive/             # Proactive features
│   │   └── schemas/               # Pydantic models
│   ├── tests/                     # Test suite
│   ├── logs/                      # Application logs
│   ├── Dockerfile                 # Container image
│   ├── docker-compose.yml         # Local development
│   └── pyproject.toml             # Python dependencies
├── ui/                            # Next.js dashboard
│   ├── src/
│   │   ├── app/                   # App Router pages
│   │   ├── components/            # React components
│   │   └── lib/                   # Utilities and hooks
│   ├── public/                    # Static assets
│   └── package.json               # Node.js dependencies
├── docs/                          # Documentation
├── infra/                         # Infrastructure
└── Makefile                       # Project automation
```

## 🎯 Definition of Done (DoD)

### Kodkvalitet
- [ ] Alla tester passerar
- [ ] Code coverage ≥80%
- [ ] Linting och formatting OK
- [ ] Type checking OK
- [ ] Security scanning OK

### Funktionell
- [ ] API endpoints fungerar
- [ ] Error handling implementerad
- [ ] Loggning implementerad
- [ ] Metrics samlas in
- [ ] Health checks OK

### Performance
- [ ] p95 latency inom SLA
- [ ] Memory usage stabil
- [ ] CPU usage optimal
- [ ] Response times mätbara

## 🔄 Utvecklingsflöde

1. **Feature branch** från main
2. **Implementera** med TDD-approach
3. **Tester** och linting
4. **Code review** och feedback
5. **Merge** till develop
6. **Integration testing**
7. **Deploy** till staging
8. **Production release**

## 📞 Support

För frågor eller support, kontakta utvecklingsteamet eller skapa en issue i projektet.

---

**Jarvis** - Intelligent AI Assistant med Edge-First Processing
