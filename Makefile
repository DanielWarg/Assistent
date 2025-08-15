.PHONY: help install dev test build clean docker docker-compose

help: ## Visa denna hjälp
	@echo "Jarvis Project - Tillgängliga kommandon:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Installera alla dependencies
	@echo "Installerar Core dependencies..."
	cd core && make install
	@echo "Installerar UI dependencies..."
	cd ui && npm install

install-prod: ## Installera endast production dependencies
	@echo "Installerar Core production dependencies..."
	cd core && make install-prod
	@echo "Installerar UI dependencies..."
	cd ui && npm install

install-dev: ## Installera development dependencies
	@echo "Installerar Core development dependencies..."
	cd core && make install-dev
	@echo "Installerar UI dependencies..."
	cd ui && npm install

dev: ## Starta utvecklingsmiljö (Core + UI)
	@echo "Startar utvecklingsmiljö..."
	@echo "Core: http://localhost:8000"
	@echo "UI: http://localhost:3000"
	@echo "Tryck Ctrl+C för att stoppa"
	@trap 'kill 0' SIGINT; \
	cd core && make dev & \
	cd ui && npm run dev & \
	wait

dev-core: ## Starta endast Core
	cd core && make dev

dev-ui: ## Starta endast UI
	cd ui && npm run dev

test: ## Kör alla tester
	@echo "Kör Core tester..."
	cd core && make test
	@echo "Kör UI tester..."
	cd ui && npm run lint

verify: ## Kör Core Go/No-Go runner
	@echo "Kör Core Go/No-Go runner..."
	cd core && make verify

verify-harden: ## Kör verify & harden + selftest
	@echo "Kör Core verify & harden + selftest..."
	cd core && make verify-harden

go-no-go: ## Kör Go/No-Go test för hybrid-readiness
	@echo "Kör Core Go/No-Go test..."
	cd core && make go-no-go

report-slowest: ## Generera rapport över långsammaste requests
	@echo "Genererar rapport över långsammaste requests..."
	cd core && make report-slowest

tls-setup: ## Skapa TLS-certifikat för hybrid-dev
	@echo "Skapar TLS-certifikat..."
	cd core && make tls-setup

tls-dev: ## Starta Core med TLS
	@echo "Startar Core med TLS..."
	cd core && make tls-dev

types: ## Generera TypeScript typer från OpenAPI
	@echo "Generera TypeScript typer..."
	cd core && curl -s http://localhost:8000/openapi.json > openapi.json
	cd ui && npx openapi-typescript ../core/openapi.json -o src/types/api.d.ts
	@echo "TypeScript typer genererade i ui/src/types/api.d.ts"

types-check: ## Kontrollera att TypeScript typer inte ändrats utan commit
	@echo "Kontrollerar TypeScript typer..."
	@if git diff --quiet ui/src/types/api.d.ts; then \
		echo "✅ TypeScript typer är uppdaterade"; \
	else \
		echo "❌ TypeScript typer har ändrats utan commit"; \
		echo "Kör 'make types' och commita ändringarna"; \
		exit 1; \
	fi

# Hybrid-ready targets
hybrid-setup: ## Komplett hybrid-setup (Core + UI + Desktop prep)
	@echo "🚀 Komplett hybrid-setup..."
	make install-prod
	make types
	@echo "✅ Hybrid-setup klar!"

hybrid-dev: ## Starta hybrid-utvecklingsmiljö
	@echo "🚀 Startar hybrid-utvecklingsmiljö..."
	@echo "Core: http://127.0.0.1:8000"
	@echo "UI: http://localhost:3000"
	@echo "Desktop: Förberedd för Tauri"
	@echo ""
	@echo "Terminal 1: cd core && make dev"
	@echo "Terminal 2: cd ui && npm run dev"
	@echo "Terminal 3: cd desktop && npm run tauri dev"

test-core: ## Kör Core tester
	cd core && make test

test-ui: ## Kör UI tester
	cd ui && npm run lint

build: ## Bygga alla komponenter
	@echo "Bygger Core..."
	cd core && make build
	@echo "Bygger UI..."
	cd ui && npm run build

build-core: ## Bygga Core
	cd core && make build

build-ui: ## Bygga UI
	cd ui && npm run build

clean: ## Rensa alla byggfiler
	@echo "Rensar Core..."
	cd core && make clean
	@echo "Rensar UI..."
	cd ui && rm -rf .next out dist
	@echo "Rensar genererade filer..."
	rm -f core/openapi.json ui/src/types/api.d.ts

docker: ## Bygga Docker images
	@echo "Bygger Core Docker image..."
	cd core && docker build -t jarvis-core:latest .

docker-compose: ## Starta med Docker Compose
	cd core && docker-compose up -d

docker-compose-down: ## Stoppa Docker Compose
	cd core && docker-compose down

logs: ## Visa loggar
	cd core && tail -f logs/*.log

status: ## Visa systemstatus
	@echo "=== Core Status ==="
	curl -s http://localhost:8000/health/live || echo "Core inte tillgänglig"
	@echo ""
	@echo "=== UI Status ==="
	curl -s http://localhost:3000 | head -n 1 || echo "UI inte tillgänglig"

setup: ## Komplett setup av projektet
	@echo "=== Jarvis Project Setup ==="
	@echo "1. Skapar virtual environment..."
	cd core && python3.11 -m venv .venv
	@echo "2. Installerar dependencies..."
	$(MAKE) install
	@echo "3. Kör tester..."
	$(MAKE) test
	@echo "4. Setup komplett!"
	@echo "Kör 'make dev' för att starta utvecklingsmiljön"
