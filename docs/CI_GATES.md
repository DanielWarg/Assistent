# 🚦 CI Gates - Jarvis Pipeline

## 🎯 Go/No-Go Runner

**Fail om p95 > SLA eller SSE brister**

```yaml
- name: Go/No-Go runner
  run: |
    cd core
    source .venv/bin/activate
    export API_KEY=dev-secret
    export CORE_BASE_URL=http://127.0.0.1:8000
    python -m src.scripts.go_no_go_runner
```

**SLA Thresholds:**
- Router p95 ≤ 500ms
- E2E p95 ≤ 1000ms
- SSE ≥ 5 events inom 5s

## 🔒 Types Check

**Fail om UI-typer inte är uppdaterade vs /openapi.json**

```yaml
- name: Types check
  run: |
    make types && git diff --exit-code ui/src/types/api.d.ts
```

**Kör automatiskt:**
- `make types` - Generera typer från OpenAPI
- `git diff` - Verifiera att inga ändringar gjorts
- Fail om typerna inte är synkroniserade

## 🧪 Playwright Smoke

**Fail om UI inte visar bas-KPI/loggflöde**

```yaml
- name: UI smoke
  run: |
    cd ui && npx playwright install --with-deps && npx playwright test
```

**Testar:**
- Översikt med KPI-kort
- Loggar med SSE-events
- Error handling (Core offline)
- Accessibility (ARIA, keyboard)

## 🔍 Pre-commit Hooks

**Fail om kodkvalitet inte uppfylls**

```yaml
- name: Pre-commit
  run: |
    cd core && pre-commit run --all-files
    cd ../ui && npm run lint
```

**Core (Python):**
- `ruff` - Linting och formatting
- `mypy` - Type checking
- `black` - Code formatting

**UI (TypeScript):**
- `eslint` - Linting
- `tsc` - Type checking
- `prettier` - Code formatting

## 📊 Performance Gates

**Fail om prestanda inte uppfyller SLA**

```yaml
- name: Performance validation
  run: |
    cd core
    source .venv/bin/activate
    # Kör selftest och validera p95
    python -m src.scripts.flow_selftest --out ./logs/flow.jsonl
    # Validera SLA
    ROUTER_P95=$(curl -sf http://127.0.0.1:8000/metrics | jq -r '.router.p95 // empty')
    if [[ "$ROUTER_P95" != "" && $(echo "$ROUTER_P95 > 0.5" | bc -l) -eq 1 ]]; then
      echo "❌ Router p95 ($ROUTER_P95) exceeds SLA (500ms)"
      exit 1
    fi
```

## 🚨 Security Gates

**Fail om säkerhet inte uppfyller krav**

```yaml
- name: Security check
  run: |
    cd core
    source .venv/bin/activate
    # PII masking validation
    python -m src.scripts.go_no_go_runner --security-only
    # API key validation
    curl -H "X-API-Key: invalid" http://127.0.0.1:8000/selftest/run
    # Should return 403
```

## 📋 Complete CI Pipeline

```yaml
name: CI Pipeline

on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd core && make install-dev
          cd ../ui && npm ci
      
      - name: Start Core
        run: |
          cd core
          source .venv/bin/activate
          nohup uvicorn src.app.main:app --host 127.0.0.1 --port 8000 >/dev/null 2>&1 &
          sleep 3
      
      - name: Go/No-Go runner
        run: |
          cd core
          source .venv/bin/activate
          export API_KEY=dev-secret
          export CORE_BASE_URL=http://127.0.0.1:8000
          python -m src.scripts.go_no_go_runner
      
      - name: Types check
        run: |
          make types && git diff --exit-code ui/src/types/api.d.ts
      
      - name: UI smoke
        run: |
          cd ui && npx playwright install --with-deps && npx playwright test
      
      - name: Pre-commit
        run: |
          cd core && pre-commit run --all-files
          cd ../ui && npm run lint
```

## 🎯 Gate Status

| Gate | Status | Fail Criteria |
|------|--------|---------------|
| **Go/No-Go** | 🟢 | p95 > SLA, SSE < min events |
| **Types Check** | 🟢 | UI typer != OpenAPI |
| **Playwright** | 🟢 | UI smoke failar |
| **Pre-commit** | 🟢 | Kodkvalitet < standard |
| **Performance** | 🟢 | p95 > threshold |
| **Security** | 🟢 | PII leak, auth fail |

## 🚀 Deployment Gates

**Production deployment kräver:**
- ✅ Alla CI gates passerar
- ✅ Security scan clean
- ✅ Performance SLA uppfylls
- ✅ Manual approval från Tech Lead

---

**Status: Ready for M1 (Media) implementation** 🎯
