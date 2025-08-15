#!/bin/bash
# TLS Setup Script for Jarvis Core (Hybrid Development)
# Skapar lokala SSL-certifikat med mkcert

set -e

echo "🔐 TLS Setup för Jarvis Core (Hybrid Development)"
echo "=================================================="

# Check if mkcert is installed
if ! command -v mkcert &> /dev/null; then
    echo "❌ mkcert är inte installerat"
    echo ""
    echo "Installera mkcert:"
    echo "  macOS: brew install mkcert nss"
    echo "  Ubuntu/Debian: sudo apt install mkcert"
    echo "  Windows: choco install mkcert"
    echo ""
    echo "Efter installation, kör detta script igen"
    exit 1
fi

# Create certs directory
CERT_DIR="./certs"
mkdir -p "$CERT_DIR"

echo "📁 Skapar certifikat i: $CERT_DIR"

# Install mkcert root CA (if not already installed)
echo "🔑 Installerar mkcert root CA..."
mkcert -install

# Generate certificates for localhost
echo "📜 Genererar certifikat för localhost..."
cd "$CERT_DIR"
mkcert localhost 127.0.0.1 ::1

# Rename to standard names
if [[ -f "localhost+2.pem" ]]; then
    mv localhost+2.pem localhost.pem
    mv localhost+2-key.pem localhost-key.pem
    echo "✅ Certifikat genererade: localhost.pem, localhost-key.pem"
elif [[ -f "localhost+1.pem" ]]; then
    mv localhost+1.pem localhost.pem
    mv localhost+1-key.pem localhost-key.pem
    echo "✅ Certifikat genererade: localhost.pem, localhost-key.pem"
else
    echo "✅ Certifikat genererade"
fi

cd ..

# Update .env file if it exists
if [[ -f ".env" ]]; then
    echo "🔧 Uppdaterar .env med TLS-konfiguration..."
    if grep -q "ENABLE_TLS" .env; then
        sed -i.bak 's/ENABLE_TLS=.*/ENABLE_TLS=true/' .env
    else
        echo "ENABLE_TLS=true" >> .env
    fi
    
    if grep -q "TLS_CERT" .env; then
        sed -i.bak "s|TLS_CERT=.*|TLS_CERT=$CERT_DIR/localhost.pem|" .env
    else
        echo "TLS_CERT=$CERT_DIR/localhost.pem" >> .env
    fi
    
    if grep -q "TLS_KEY" .env; then
        sed -i.bak "s|TLS_KEY=.*|TLS_KEY=$CERT_DIR/localhost-key.pem|" .env
    else
        echo "TLS_KEY=$CERT_DIR/localhost-key.pem" >> .env
    fi
    
    echo "✅ .env uppdaterad med TLS-konfiguration"
else
    echo "⚠️  .env fil hittades inte - skapa den manuellt med:"
    echo "   ENABLE_TLS=true"
    echo "   TLS_CERT=$CERT_DIR/localhost.pem"
    echo "   TLS_KEY=$CERT_DIR/localhost-key.pem"
fi

echo ""
echo "🎉 TLS Setup klar!"
echo ""
echo "Nu kan du starta Core med TLS:"
echo "  make tls-dev"
echo ""
echo "Eller manuellt:"
echo "  uvicorn src.app.main:app --ssl-keyfile $CERT_DIR/localhost-key.pem --ssl-certfile $CERT_DIR/localhost.pem --host 127.0.0.1 --port 8000"
echo ""
echo "UI kan nu använda: https://localhost:8000"
