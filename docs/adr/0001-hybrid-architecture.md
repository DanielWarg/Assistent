# ADR 0001: Hybrid Architecture

## Status
Accepted

## Context
Jarvis behöver en arkitektur som stöder både lokal utveckling och hybrid-deployment med desktop-applikationer. Systemet ska kunna köra som:
- Lokal utvecklingsmiljö (Core + UI)
- Desktop-app med inbyggd Core
- Edge-noder med Core API

## Decision
Implementera en **hybrid-arkitektur** med separerade lager:

### Arkitektur
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Desktop App   │    │   Web Dashboard │    │   Edge Nodes    │
│   (Tauri)      │    │   (Next.js)     │    │   (Raspberry Pi)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Core API      │
                    │   (FastAPI)     │
                    └─────────────────┘
```

### Komponenter
1. **Core API** - FastAPI backend med router-first approach
2. **UI Dashboard** - Next.js för webb-övervakning
3. **Desktop App** - Tauri för lokala desktop-funktioner
4. **Edge Nodes** - Lättviktiga Core-instanser för IoT

## Consequences

### Positiva
- **Flexibilitet** - Olika deployment-modeller
- **Skalbarhet** - Kan köra på olika plattformar
- **Utveckling** - En kodbas för alla lager
- **Säkerhet** - Lokal bearbetning av känslig data

### Negativa
- **Komplexitet** - Flera lager att underhålla
- **Testing** - Behöver testa alla kombinationer
- **Deployment** - Olika paketering för olika plattformar
- **Synchronisering** - API-kontrakt måste hållas synkroniserade

### Risker
- **API-drift** - Core och UI kan divergera
- **Performance** - Desktop-app kan bli tung
- **Maintenance** - Flera codebases att underhålla

## Implementation

### Faser
1. **M0** - Core API med grundläggande funktionalitet ✅
2. **M1** - UI Dashboard med SSE och metrics ✅
3. **M2** - Desktop App med Tauri ✅
4. **M3** - Edge Nodes med lättviktig Core

### Tekniska Beslut
- **API-first** - Alla funktioner exponeras via REST API
- **SSE för realtid** - Server-Sent Events för loggning
- **TLS lokalt** - HTTPS för säker kommunikation
- **Health gates** - Validering innan app-start
- **PII-maskning** - Automatisk maskning av känslig data

### Standards
- **OpenAPI 3.0** - API-kontrakt
- **JSONL logging** - Strukturerad loggning
- **Correlation IDs** - Request tracking
- **SLA-mätning** - p50/p95/p99 latens

## Alternativ Betraktade

### Monolitisk App
- **Fördelar**: Enklare att utveckla
- **Nackdelar**: Svårare att skala, mindre flexibel

### Microservices
- **Fördelar**: Hög skalbarhet
- **Nackdelar**: Överkomplexitet för lokalt system

### Event-driven
- **Fördelar**: Löst kopplade komponenter
- **Nackdelar**: Svårare att debugga, eventual consistency

## Referenser
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Tauri Documentation](https://tauri.app/)
- [Next.js Documentation](https://nextjs.org/)
- [ADR Template](https://adr.github.io/madr/)

---

**Datum**: 2024-08-15  
**Beslutstagare**: Utvecklingsteam  
**Granskare**: Tech Lead
