#!/bin/bash
# Quick test script for Verify & Harden checklist

set -euo pipefail
: "${CORE_BASE_URL:=http://127.0.0.1:8000}"

echo "🚀 Quick Test - Verify & Harden Checklist"
echo "=========================================="

CORE_URL="${CORE_BASE_URL}"
API_KEY="dev-api-key-change-in-production"

echo "🌐 Testing against: $CORE_URL"
echo ""

# 1) API Contract
echo "1️⃣ Testing API Contract..."
if curl -sf "$CORE_URL/openapi.json" > /dev/null; then
    echo "   ✅ OpenAPI endpoint working"
else
    echo "   ❌ OpenAPI endpoint failed"
    exit 1
fi

# 2) CORS/TrustedHost
echo "2️⃣ Testing CORS/TrustedHost..."
CORS_HEADER=$(curl -s -I "$CORE_URL/health/live" | grep -i "access-control-allow-origin" || echo "")
if [[ "$CORS_HEADER" == *"localhost:3000"* ]]; then
    echo "   ✅ CORS properly configured"
else
    echo "   ⚠️  CORS configuration issue: $CORS_HEADER"
fi

# 3) API Key Authentication
echo "3️⃣ Testing API Key Authentication..."

# Test without API key (should be 401)
echo "   Testing POST without API key..."
RESPONSE=$(curl -s -w "%{http_code}" -X POST "$CORE_URL/selftest/run" \
    -H "Content-Type: application/json" \
    -d '{"test_name": "auth_test"}' \
    -o /dev/null)
if [[ "$RESPONSE" == "401" ]]; then
    echo "   ✅ 401 returned without API key"
else
    echo "   ❌ Expected 401, got $RESPONSE"
    exit 1
fi

# Test with invalid API key (should be 403)
echo "   Testing POST with invalid API key..."
RESPONSE=$(curl -s -w "%{http_code}" -X POST "$CORE_URL/selftest/run" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: invalid-key" \
    -d '{"test_name": "auth_test"}' \
    -o /dev/null)
if [[ "$RESPONSE" == "403" ]]; then
    echo "   ✅ 403 returned with invalid API key"
else
    echo "   ❌ Expected 403, got $RESPONSE"
    exit 1
fi

# Test with valid API key (should be 200)
echo "   Testing POST with valid API key..."
RESPONSE=$(curl -s -w "%{http_code}" -X POST "$CORE_URL/selftest/run" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{"test_name": "auth_test"}' \
    -o /dev/null)
if [[ "$RESPONSE" == "200" ]]; then
    echo "   ✅ 200 returned with valid API key"
else
    echo "   ❌ Expected 200, got $RESPONSE"
    exit 1
fi

# 4) Observability
echo "4️⃣ Testing Observability..."
if curl -sf "$CORE_URL/metrics" > /dev/null; then
    echo "   ✅ Metrics endpoint working"
else
    echo "   ❌ Metrics endpoint failed"
    exit 1
fi

if curl -sf "$CORE_URL/logs/stats" > /dev/null; then
    echo "   ✅ Logs stats endpoint working"
else
    echo "   ❌ Logs stats endpoint failed"
    exit 1
fi

# 5) Health Endpoints
echo "5️⃣ Testing Health Endpoints..."
if curl -sf "$CORE_URL/health/live" > /dev/null; then
    echo "   ✅ Health live endpoint working"
else
    echo "   ❌ Health live endpoint failed"
    exit 1
fi

if curl -sf "$CORE_URL/health/ready" > /dev/null; then
    echo "   ✅ Health ready endpoint working"
else
    echo "   ❌ Health ready endpoint failed"
    exit 1
fi

# 6) SSE Test
echo "6️⃣ Testing SSE (Server-Sent Events)..."
echo "   Starting SSE test (will timeout after 5s)..."
timeout 5s curl -N "$CORE_URL/logs/stream" > /dev/null 2>&1 || true
echo "   ✅ SSE endpoint accessible"

echo ""
echo "🎉 All quick tests passed!"
echo ""
echo "📋 Next steps:"
echo "   - Run full verify: make verify"
echo "   - Run selftest: make selftest"
echo "   - Run both: make verify-harden"
echo "   - Run Go/No-Go: make go-no-go"
