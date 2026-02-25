#!/bin/bash

# 🏁 ODISEO TEST RUNNER
# Ejecuta todos los tests funcionales del MVP

echo "🚀 INICIANDO TEST RUNNER ODISEO..."
echo "=================================="

# Env vars dummy para testing
export STRIPE_SECRET_KEY="sk_test_dummy"
export STRIPE_WEBHOOK_SECRET="whsec_dummy"
export TELEGRAM_BOT_TOKEN="123456:dummy"
export TELEGRAM_CHAT_ID="-123456"
export NEXTAUTH_SECRET="secret_dummy"
export NEXT_PUBLIC_APP_URL="http://localhost:3000"

FAILED=0

# 1. Test Telegram (Python)
echo ""
python tools/test_telegram.py
if [ $? -ne 0 ]; then
    echo "❌ TEST TELEGRAM FALLIDO"
    FAILED=$((FAILED + 1))
else
    echo "✅ TEST TELEGRAM PASADO"
fi

# 2. Test Stripe (TS)
echo ""
npx tsx web/tests/stripe.test.ts
STATUS=$?
if [ $STATUS -eq 0 ]; then
    echo "✅ TEST STRIPE PASADO"
else
    echo "❌ TEST STRIPE FALLIDO (Code: $STATUS)"
    FAILED=$((FAILED + 1))
fi

# 3. Test Auth (TS)
echo ""
npx tsx web/tests/auth.test.ts
STATUS=$?
if [ $STATUS -eq 0 ]; then
    echo "✅ TEST AUTH PASADO"
else
    echo "❌ TEST AUTH FALLIDO (Code: $STATUS)"
    FAILED=$((FAILED + 1))
fi

# 4. Test Landing (TS)
echo ""
npx tsx web/tests/landing.test.ts
STATUS=$?
if [ $STATUS -eq 0 ]; then
    echo "✅ TEST LANDING PASADO"
else
    echo "❌ TEST LANDING FALLIDO (Code: $STATUS)"
    FAILED=$((FAILED + 1))
fi

echo ""
echo "=================================="
if [ $FAILED -eq 0 ]; then
    echo "✅ TODOS LOS TESTS PASANDO (MVP READY)"
    exit 0
else
    echo "❌ SE ENCONTRARON $FAILED TESTS ROTOS"
    exit 1
fi
