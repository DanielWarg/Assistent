# 🎯 Hybrid Ready Checklist - Jarvis Core

Denna checklista säkerställer att Jarvis Core är 100% redo för hybrid-deployment.

## 🚀 Snabb Slutkontroll (Rekommenderad Rutin)

### 1. Starta Utvecklingsmiljö
```bash
make dev  # Core + UI
```

### 2. Kör Go/No-Go Test
```bash
make verify  # Validerar hybrid-readiness
```

### 3. Kör Selftest A→Ö
```bash
make selftest  # Komplett systemtest
```

### 4. Analysera Prestanda
```bash
make report-slowest  # Top 10 långsammaste requests
```

### 5. Commita Rapporter (Valfritt)
```bash
git add logs/*.md logs/*.json
git commit -m "feat: hybrid-ready validation reports"
```

---

## ✅ Hybrid Ready Kriterier

### 🔒 Säkerhet & Policy
- [ ] **API-nyckel autentisering** - Muterande endpoints kräver `X-API-Key`
- [ ] **CORS/TrustedHost** - Endast UI-origin tillåten
- [ ] **Rate limiting** - 2 req/s på POST endpoints
- [ ] **Security headers** - CSP, XSS, X-Frame-Options
- [ ] **PII-maskning** - Email, telefon, JWT, IBAN, OAuth

### 📊 Observability
- [ ] **Ringbuffer med backpressure** - Konfigurerbar storlek, aldrig hänger SSE
- [ ] **Correlation-ID** - `X-Request-ID` propagieras genom hela flödet
- [ ] **Strukturerad loggning** - JSONL med `rid`, `lat_ms`, `status`
- [ ] **Metrics endpoints** - Router, E2E, errors, system
- [ ] **Log rotation** - 20MB x10 + retention policies

### 🧪 Testing & Validation
- [ ] **Go/No-Go Runner** - Automatisk SLA-validering (p95 ≤ 500ms)
- [ ] **Selftest A→Ö** - Health → metrics → SSE → router → tools
- [ ] **SSE stabilitetstest** - 2 parallella läsare, 200 requests
- [ ] **API kontrakt** - OpenAPI generering och validering
- [ ] **Performance testing** - p50/p95/p99 mätning

### 🏗️ Robusthet & Lifecycle
- [ ] **Graceful shutdown** - SIGTERM/SIGINT hantering
- [ ] **Health separation** - `/health/live` vs `/health/ready`
- [ ] **Port management** - Tydliga felmeddelanden vid konflikter
- [ ] **Error handling** - Global exception handler med logging
- [ ] **Middleware stack** - Timing, Request-ID, Rate limiting

### 🔐 TLS & Hybrid Development
- [ ] **mkcert setup** - Lokala SSL-certifikat för development
- [ ] **TLS konfiguration** - Env-baserad aktivering
- [ ] **HTTPS support** - Core kan köra med SSL
- [ ] **Certificate management** - Automatisk .env uppdatering

---

## 🛠️ Verifieringsverktyg

### Snabb Test
```bash
cd core
./quick_test.sh
```

### Go/No-Go Runner
```bash
make verify          # Komplett hybrid-readiness test
make verify-harden   # Selftest + Go/No-Go
```

### Performance Analys
```bash
make report-slowest  # Top 10 långsammaste requests
```

### TLS Setup
```bash
make tls-setup      # Skapa SSL-certifikat
make tls-dev        # Starta med TLS
```

---

## 📊 Acceptanskriterier

### 🟢 GO (Hybrid Ready)
- ✅ Alla Go/No-Go tester passerar
- ✅ Selftest A→Ö passerar
- ✅ p95 inom SLA (≤500ms)
- ✅ SSE stabil under stress
- ✅ API-nyckel autentisering fungerar
- ✅ PII-maskning verifierad
- ✅ TLS setup tillgängligt

### 🟡 WARNING (Nästan Ready)
- ⚠️ Enstaka tester varnar men passerar
- ⚠️ p95 nära SLA-gräns
- ⚠️ Ringbuffer använder >80% kapacitet
- ⚠️ TLS inte konfigurerat

### 🔴 NO-GO (Inte Ready)
- ❌ Något Go/No-Go test misslyckas
- ❌ Selftest misslyckas
- ❌ p95 över SLA
- ❌ SSE kraschar under stress
- ❌ API-nyckel autentisering fungerar inte
- ❌ PII läcker i loggar

---

## 🎯 Definition of Done (Hybrid)

**Klar enligt DoD:**
- [ ] Alla Go/No-Go tester passerar
- [ ] Selftest A→Ö passerar med p95 inom SLA
- [ ] SSE fungerar stabilt under stress
- [ ] API-nyckel autentisering verifierad
- [ ] PII-maskning testad och fungerar
- [ ] Ringbuffer backpressure testad
- [ ] Correlation-ID propagation verifierad
- [ ] Health endpoints separerade och fungerar
- [ ] Rate limiting testad på muterande endpoints
- [ ] TLS setup tillgängligt för hybrid development

**Då är Jarvis Core 100% hybrid-redo!** 🚀

---

## 📋 Daglig Utvecklingsloop

```bash
# 1. Starta utvecklingsmiljö
make dev

# 2. Utveckla och testa
make test
make lint
make format

# 3. Validera hybrid-readiness
make verify

# 4. Kör fullständig validering
make verify-harden

# 5. Analysera prestanda
make report-slowest

# 6. Commita och pusha
git add .
git commit -m "feat: [description]"
git push
```

**Nu är du redo för hybrid-deployment!** ✨
