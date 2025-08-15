# 🖥️ Jarvis Desktop App

Desktop-applikation för Jarvis med Tauri (Rust + Web Technologies).

## 🚀 Snabbstart

### Förutsättningar
- Rust (latest stable)
- Node.js 18+
- Core API körs på `http://127.0.0.1:8000`

### Installation
```bash
# Installera Tauri CLI
cargo install tauri-cli

# Installera dependencies
npm install

# Starta utvecklingsmiljö
npm run tauri dev
```

### Bygga för produktion
```bash
npm run tauri build
```

## 🔧 Konfiguration

### Environment Variables
```bash
# Core API URL
CORE_BASE_URL=http://127.0.0.1:8000

# API Key för autentisering
API_KEY=your-api-key
```

### Tauri Config (`src-tauri/tauri.conf.json`)
```json
{
  "tauri": {
    "bundle": {
      "identifier": "com.jarvis.desktop",
      "icon": ["icons/32x32.png", "icons/128x128.png", "icons/128x128@2x.png"]
    },
    "security": {
      "csp": "default-src 'self'; connect-src 'self' http://127.0.0.1:8000"
    }
  }
}
```

## 🚀 Autostart

### macOS (launchd)
```bash
# Installera launchd plist
sudo cp infra/launchd/jarvis.plist /Library/LaunchDaemons/
sudo launchctl load /Library/LaunchDaemons/jarvis.plist
```

### Windows (Task Scheduler)
```bash
# Skapa schemalagd uppgift för autostart
schtasks /create /tn "Jarvis Desktop" /tr "path\to\jarvis-desktop.exe" /sc onlogon
```

### Linux (systemd)
```bash
# Installera systemd service
sudo cp infra/systemd/jarvis-desktop.service /etc/systemd/system/
sudo systemctl enable jarvis-desktop
sudo systemctl start jarvis-desktop
```

## 🔍 Health Gate

Desktop-appen kontrollerar Core API innan start:

1. **Health Check** - Testar `/health/live` endpoint
2. **API Status** - Verifierar `/info` endpoint
3. **Fallback** - Visar felbanner med retry-knapp

### Felhantering
```typescript
// Exempel på health gate implementation
async function checkCoreHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${CORE_BASE_URL}/health/live`);
    return response.ok;
  } catch (error) {
    console.error('Core API inte tillgänglig:', error);
    return false;
  }
}
```

## 📱 Features

- **Mikrofonstyrning** - Voice commands via Core API
- **Notifieringar** - System notifications för viktiga händelser
- **Menystart** - Snabbåtkomst till vanliga kommandon
- **Autostart** - Startar automatiskt med systemet
- **Health Monitoring** - Kontrollerar Core API status

## 🧪 Testing

```bash
# Kör tester
npm test

# E2E tester med Playwright
npx playwright test

# Build test
npm run tauri build
```

## 📦 Distribution

### macOS
```bash
npm run tauri build
# Genererar .dmg fil i src-tauri/target/release/bundle/dmg/
```

### Windows
```bash
npm run tauri build
# Genererar .msi fil i src-tauri/target/release/bundle/msi/
```

### Linux
```bash
npm run tauri build
# Genererar .deb och .AppImage filer
```

## 🔒 Säkerhet

- **CSP** - Content Security Policy för säker rendering
- **API Key** - Autentisering mot Core API
- **Local Only** - Endast lokala anslutningar tillåts
- **Sandbox** - Tauri sandbox för säker körning

## 📚 Utveckling

### Projektstruktur
```
desktop/
├── src/                    # React/TypeScript kod
├── src-tauri/             # Rust backend
│   ├── src/               # Rust källkod
│   ├── Cargo.toml         # Rust dependencies
│   └── tauri.conf.json    # Tauri konfiguration
├── public/                 # Statiska filer
└── package.json            # Node.js dependencies
```

### Vanliga kommandon
```bash
# Utveckling
npm run tauri dev

# Build
npm run tauri build

# Lint
npm run lint

# Test
npm test
```

## 🆘 Support

För frågor eller problem:
1. Kontrollera att Core API körs
2. Verifiera environment variables
3. Kontrollera Tauri logs
4. Skapa issue i projektet

---

**Jarvis Desktop** - Intelligent AI Assistant för ditt skrivbord 🚀
