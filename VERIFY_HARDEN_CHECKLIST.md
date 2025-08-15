# 🚀 Verify & Harden Checklist - Jarvis Core

Denna checklista säkerställer att Jarvis Core är 100% hybrid-redo innan vi springer vidare.

## 📋 Snabb "Go/No-Go" Körning

### 1. Core Upp
```bash
cd core && source .venv/bin/activate || python3 -m venv .venv && source .venv/bin/activate
pip install -e . pytest requests
make run
```

### 2. API Kontrakt & SSE
```bash
curl -sf http://127.0.0.1:8000/health/ready
curl -sf http://127.0.0.1:8000/openapi.json | jq .info
curl -N  http://127.0.0.1:8000/logs/stream | head -n 5
```

### 3. Selftest & SLA
```bash
make selftest
curl -sf http://127.0.0.1:8000/metrics | jq .
# bekräfta p95 inom budget – annars: RED
```

---

## 🔍 Detaljerad Verifiering

### ✅ 1) Sanity & Kontrakt

- [ ] **API-kontrakt låst:** `GET /openapi.json` svarar 200 och genererar TS-typer i UI (`make types`)
- [ ] **CORS/TrustedHost:** I dev endast `http://localhost:3000` (UI) + `localhost`/`127.0.0.1`
- [ ] **API-nyckel:** Muterande endpoints returnerar **401** utan `X-API-Key` och **200** med korrekt nyckel

**Snabbtest:**
```bash
# Kör quick test script
./quick_test.sh

# Eller manuellt:
curl -i http://127.0.0.1:8000/metrics
curl -i -X POST http://127.0.0.1:8000/selftest/run           # ska vara 401
curl -i -H "X-API-Key: ${API_KEY}" -X POST http://127.0.0.1:8000/selftest/run  # 200
```

### ✅ 2) Observability på Riktigt

- [ ] **Ringbuffer backpressure:** `LOG_BUFFER_MAX` i `.env`, droppar äldsta, aldrig hänger SSE
- [ ] **Correlation-ID:** `X-Request-ID` propagieras och syns i: HTTP-logg → router → tool → JSONL
- [ ] **PII-maskning:** e-post, telefon, tokens (JWT), IBAN; verifiera i JSONL att inget rått läcker
- [ ] **Rotation/retention:** 20MB x10 + rensning >N dagar

**SSE-stresstest:**
```bash
# starta 2–3 parallella läsare
curl -N http://127.0.0.1:8000/logs/stream >/dev/null &
curl -N http://127.0.0.1:8000/logs/stream >/dev/null &
# generera trafik (100 req)
for i in $(seq 1 100); do curl -s http://127.0.0.1:8000/health/live >/dev/null; done
# kontroll: inga häng, CPU stabil, minne stabilt
```

### ✅ 3) SLA-gate (Selftest A→Ö)

- [ ] **p95-latens** under era mål (router/e2e) valideras i `flow_selftest.py` och **failar CI** om över budget
- [ ] **SSE-prova**: selftest öppnar SSE och bekräftar minst N logg-event inom T sek
- [ ] **Rapport**: genererar `logs/selftest_{ts}.json` + `.md` med KPI-sammanfattning

**CI-krok (idé):**
```yaml
# Kör core i bakgrunden → kör selftest → `GET /metrics` → assert `p95 <= budget`
```

### ✅ 4) Robusthet (Hybrid)

- [ ] **Graceful shutdown:** SIGTERM/SIGINT flushar ringbuffer och stänger SSE snyggt
- [ ] **Port-konflikt:** Startlogg säger tydligt om port upptagen (och exit kod ≠ 0)
- [ ] **Health separation:** `/health/live` = process up, `/health/ready` = router & orchestrator initierade
- [ ] **Rate limiting:** 2 req/s token-bucket på POST endpoints (dev kan vara högre)

**Drill:**
```bash
# döda och starta om core medan UI's loggsida är öppen – ser du "Disconnected" → auto-reconnect → åter ström?
pkill -f uvicorn && make -C core run
```

### ✅ 5) UI-härdning

- [ ] **SSE-reconnect** med exponentiell backoff och "Disconnected" chip
- [ ] **Error/empty states** för overview/logs/selftest
- [ ] **OpenAPI→TS typer** genereras i CI och lokalt (`make types`)
- [ ] **A11y/Perf**: ESLint a11y-regler + Lighthouse budget (min. PWA 80+ i dev)

### ✅ 6) Desktop-hybrid Förberedelse

- [ ] **TLS lokalt** (mkcert) så UI kan köra `https://localhost` och prata säkert med core
- [ ] **Autostart core**: `launchd`-plist (macOS) eller enkel startscript för dev
- [ ] **Service discovery**: UI läser core-URL från env och visar tydligt fel om core inte kör

### ✅ 7) Root-automation & Docs

- [ ] **Root Makefile**: `setup`, `dev` (kör core+ui), `fmt`, `lint`, `test`, `selftest`, `types`
- [ ] **.env.example** i **både** `/core` och `/ui` + README med exakt startsekvens
- [ ] **ADR** för större val (hybrid, SSE, API-nyckel, ringbuffer)

---

## 🛠️ Verifieringsverktyg

### Quick Test Script
```bash
cd core
./quick_test.sh
```

### Full Verify & Harden
```bash
cd core
make verify          # Kör alla verifieringstester
make verify-harden   # Kör verify + selftest
```

### Root Level
```bash
make verify          # Kör Core verify & harden
make verify-harden   # Kör Core verify + selftest
```

---

## 🚨 Felsökningsordning

### Om något faller:

1. **CORS/TrustedHost** (UI når inte core): kontrollera `CORS_ORIGINS` i `.env`
2. **401 på POST**: saknad/inkorrekt `X-API-Key`
3. **SSE dör**: ringbuffer size/backpressure, nätverksproxy, reconnect-logik i UI
4. **p95 över budget**: mät var tiden spenderas (middleware timar router vs e2e), öka cache, sänk loggvolym, optimera JSONL

---

## 📊 Acceptanskriterier

### Grön (Go):
- ✅ Alla verify-tester passerar
- ✅ Selftest passerar med p95 inom SLA
- ✅ SSE fungerar stabilt under stress
- ✅ API-nyckel autentisering fungerar
- ✅ PII-maskning verifierad

### Gul (Varning):
- ⚠️  Enstaka tester varnar men passerar
- ⚠️  p95 nära SLA-gräns
- ⚠️  Ringbuffer använder >80% kapacitet

### Röd (No-Go):
- ❌ Något verify-test misslyckas
- ❌ Selftest misslyckas eller p95 över SLA
- ❌ SSE hänger eller kraschar
- ❌ API-nyckel autentisering fungerar inte
- ❌ PII läcker i loggar

---

## 🎯 Definition of Done (DoD)

**Klar enligt DoD:**
- [ ] Alla verify-tester passerar
- [ ] Selftest passerar med p95 inom SLA
- [ ] SSE fungerar stabilt under stress
- [ ] API-nyckel autentisering verifierad
- [ ] PII-maskning testad och fungerar
- [ ] Ringbuffer backpressure testad
- [ ] Correlation-ID propagation verifierad
- [ ] Health endpoints separerade och fungerar
- [ ] Rate limiting testad på muterande endpoints

**Då är Jarvis Core 100% hybrid-redo!** 🚀
