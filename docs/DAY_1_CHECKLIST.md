# 🌅 Day-1 Checklist - Jarvis Development

## 🚀 Preflight (5 min)

```bash
# 1. Pull senaste ändringar
git pull origin master

# 2. Rensa gamla artefakter
make clean

# 3. Verifiera miljö
python3.11 --version  # Måste vara 3.11+
node --version         # Måste vara 18+
```

## 🔧 Miljö Setup (10 min)

### Core
```bash
cd core
python3.11 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .[dev]
```

### UI
```bash
cd ../ui
pnpm install  # eller npm install / yarn
```

## 🏃‍♂️ Starta Development (5 min)

```bash
# Terminal 1: Core API
cd core && make dev

# Terminal 2: UI Dashboard  
cd ui && pnpm dev
```

## ✅ Verifiera Baseline (10 min)

```bash
# 1. Kontrakt & typer
make types          # Generera TypeScript typer från OpenAPI
git add ui/src/types/api.d.ts

# 2. Selftest & Go/No-Go
make selftest       # A→Ö självtest (JSONL/MD rapporter)
make verify         # Go/No-Go: OpenAPI, auth, SSE, p95 SLA
make report-slowest # Top 10 långsammaste requests

# 3. UI smoke (Playwright)
cd ui && npx playwright test
```

## 🎯 Definition of Done - Day 1

- ✅ `make verify` **GRÖN** (p95 ≤ SLA, SSE ≥ min events)
- ✅ `make selftest` producerar rapporter i `./logs/`
- ✅ `make report-slowest` genererar MD med top-10
- ✅ UI smoke passerar alla tester
- ✅ TypeScript typer synkroniserade med OpenAPI

## 🚨 Vanliga Fallgropar

| Problem | Lösning |
|---------|---------|
| Port 8000 upptagen | `lsof -ti:8000 \| xargs kill -9` eller `make tls-dev` |
| UI CORE_BASE_URL fel | Använd `/_core/*` proxy eller `NEXT_PUBLIC_CORE_BASE_URL` |
| SSE disconnects | Kontrollera exponential backoff i UI-hook |
| PII-mask läcker | Kör `make selftest` och verifiera JSONL |

## 📊 Quick Health Check

```bash
# Core health
curl -s http://127.0.0.1:8000/health/live | jq

# UI status
curl -s http://localhost:3000 | grep -q "Jarvis"

# Performance
make report-slowest | head -20
```

## 🔒 Security Check

```bash
# API key fungerar
curl -H "X-API-Key: dev-api-key-change-in-production" \
     http://127.0.0.1:8000/selftest/status

# CSP headers
curl -s -I http://localhost:3000 | grep -i "content-security-policy"
```

## 📝 Nästa Steg

1. **Green Gate** - Alla checks passerar
2. **M1 (Media)** - Börja implementera media-funktionalitet
3. **Daily sync** - Kör denna checklist varje morgon

---

**Tid: ~30 min totalt**  
**Status: Ready for M1** 🚀
