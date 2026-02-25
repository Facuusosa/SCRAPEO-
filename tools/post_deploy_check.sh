#!/bin/bash

# 🩺 ODISEO POST-DEPLOY CHECK
# Valida que el servicio en producción esté saludable

URL=${1:-"https://odiseo.app"}
API_HEALTH="$URL/api/health"

echo "🩺 Verificando estado de producción en $URL..."

# 1. Check HTTP Status
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_HEALTH")

if [ "$HTTP_STATUS" -ne 200 ]; then
    echo "❌ ERROR: Health Check devolvió HTTP $HTTP_STATUS"
    exit 1
fi

# 2. Check JSON Response
HEALTH_JSON=$(curl -s "$API_HEALTH")
ALL_OK=$(echo "$HEALTH_JSON" | grep -o '"status":"healthy"')

if [ -z "$ALL_OK" ]; then
    echo "⚠️ STATUS DEGRADADO detectado!"
    echo "$HEALTH_JSON"
    exit 1
fi

echo "✅ PRODUCCIÓN SALUDABLE: Todos los sistemas operativos."
echo "$HEALTH_JSON"
exit 0
