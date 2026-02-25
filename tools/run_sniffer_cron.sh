#!/bin/bash

# 🏁 ODISEO SNIFFER CRON
# Ejecuta el sniffer principal y alerta en caso de fallos persistentes

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "[$(date)] 🚀 Iniciando SCAN programado..."

# Ejecutar vía Resilience Guardian para mayor estabilidad
python3 "$ROOT_DIR/scrapers/error_resilience.py" "$ROOT_DIR/targets/fravega/sniffer_fravega_v2.py"

EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "[$(date)] ❌ SCAN FALLIDO (Code: $EXIT_CODE)"
    
    # Alerta Admin via Telegram (usando curl simple para no depender de librerías en el cron)
    MESSAGE="⚠️ ODISEO CRITICAL: Sniffer en Railway falló (Code: $EXIT_CODE). Revisa logs."
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d "chat_id=$TELEGRAM_ADMIN_CHAT_ID" \
        -d "text=$MESSAGE"
else
    echo "[$(date)] ✅ SCAN COMPLETADO EXITOSAMENTE"
fi
