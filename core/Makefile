.PHONY: help install dev test lint format clean run metrics sse selftest

help: ## Visa denna hjälp
	@echo "Tillgängliga kommandon:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Installera dependencies
	python -m pip install -U pip
	pip install -e ".[dev]"

install-prod: ## Installera endast production dependencies
	python -m pip install -U pip
	pip install -r requirements.txt

install-dev: ## Installera development dependencies
	python -m pip install -U pip
	pip install -r requirements-dev.txt

dev: ## Starta utvecklingsservern
	uvicorn src.app.main:app --reload --host 127.0.0.1 --port 8000

test: ## Kör tester
	pytest tests/ -v --cov=src --cov-report=term-missing

lint: ## Kör linting
	ruff check src/ tests/
	mypy src/

format: ## Formatera kod
	black src/ tests/
	ruff format src/ tests/

clean: ## Rensa cache och logs
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf logs/*.log

run: ## Starta produktionsservern
	uvicorn src.app.main:app --host 127.0.0.1 --port 8000

metrics: ## Hämta metrics
	curl -sf http://127.0.0.1:8000/metrics | jq .

sse: ## Testa SSE-logs
	curl -N http://127.0.0.1:8000/logs/stream | head -n 5

selftest: ## Kör selftest
	python -m src.scripts.flow_selftest --out ./logs/flow.jsonl --core-url http://127.0.0.1:8000

selftest-report: ## Kör selftest och generera rapport
	python -m src.scripts.flow_selftest --out ./logs/flow.jsonl --core-url http://127.0.0.1:8000
	@echo "Rapport genererad: ./logs/flow.md och ./logs/flow.json"

verify: ## Kör Go/No-Go runner
	CORE_BASE_URL?=http://127.0.0.1:8000 API_KEY=$${API_KEY} \
	python -m src.scripts.go_no_go_runner || exit 1

verify-harden: selftest verify
	@echo "Verify & Harden klar"

go-no-go: ## Kör Go/No-Go test för hybrid-readiness
	./go_no_go_test.sh

report-slowest: ## Generera rapport över långsammaste requests
	LOG_DIR=./logs REPORT_OUT=./logs \
	python -m src.scripts.report_slowest

tls-setup: ## Skapa TLS-certifikat för hybrid-dev
	./setup_tls.sh

tls-dev: ## Starta Core med TLS (kräver tls-setup)
	@if [ ! -f "./certs/localhost.pem" ] || [ ! -f "./certs/localhost-key.pem" ]; then \
		echo "❌ TLS-certifikat saknas. Kör 'make tls-setup' först."; \
		exit 1; \
	fi
	uvicorn src.app.main:app --ssl-keyfile ./certs/localhost-key.pem --ssl-certfile ./certs/localhost.pem --reload --host 127.0.0.1 --port 8000
