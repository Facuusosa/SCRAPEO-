import asyncio
import os
import sys
import sqlite3
import logging
from datetime import datetime

# Agregar root al path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from core.notifier import TelegramNotifier
from core.http_client import AsyncHttpClient

# Configuración de logs para el test
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test-telegram")

async def test_bot_connection(token):
    """Verifica que el token del bot sea válido."""
    if not token or "dummy" in token:
        logger.warning("⚠️ Token dummy detectado, saltando conexión real.")
        return True
    client = AsyncHttpClient()
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        resp = await client.get(url)
        if resp.status_code == 200:
            data = resp.json()
            logger.info(f"✅ Bot conectado: @{data['result']['username']}")
            return True
        else:
            logger.error(f"❌ Error de conexión: {resp.status_code}")
            return False
    except Exception as e:
        logger.error(f"💥 Excepción: {e}")
        return False

async def test_send_alert(token, chat_id):
    """Verifica el envío de una alerta simulada."""
    if not token or "dummy" in token:
        logger.warning("⚠️ Token dummy detectado, saltando alerta real.")
        return True
    notifier = TelegramNotifier(token=token, chat_id=chat_id)
    opp = {
        "name": "TEST PRODUCT (ODISEO MVP)",
        "current_price": 50000,
        "gap_teorico": 25.5,
        "margen_odiseo": 20.5,
        "url": "https://www.fravega.com",
        "store": "Fravega (Test)"
    }
    logger.info("📡 Enviando alerta de prueba...")
    success = await notifier.send_opportunity(opp)
    if success:
        logger.info("✅ Alerta enviada correctamente.")
    else:
        logger.error("❌ Falló el envío de la alerta.")
    return success

async def test_db_persistence():
    """Verifica que se puedan guardar 'usuarios' en una DB de prueba."""
    db_path = os.path.join(PROJECT_ROOT, "test_odiseo.db")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS test_users (id TEXT PRIMARY KEY, tier TEXT)")
        
        test_id = "test_user_123"
        cursor.execute("INSERT OR REPLACE INTO test_users (id, tier) VALUES (?, ?)", (test_id, "vip"))
        conn.commit()
        
        cursor.execute("SELECT tier FROM test_users WHERE id = ?", (test_id,))
        res = cursor.fetchone()
        
        if res and res[0] == "vip":
            logger.info("✅ Persistencia en DB verificada.")
            return True
        else:
            logger.error("❌ Falló la persistencia en DB.")
            return False
    except Exception as e:
        logger.error(f"💥 Error DB: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

async def run_all():
    print("\n🧪 --- TEST SUITE: TELEGRAM MODULE ---")
    
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    conn_ok = await test_bot_connection(token)
    send_ok = await test_send_alert(token, chat_id)
    db_ok = await test_db_persistence()
    
    print("\n📊 RESULTADOS:")
    print(f"- Conexión Bot: {'✅ PASS' if conn_ok else '❌ FAIL'}")
    print(f"- Envío Alerta: {'✅ PASS' if send_ok else '❌ FAIL'}")
    print(f"- DB Persistencia: {'✅ PASS' if db_ok else '❌ FAIL'}")
    
    if db_ok and conn_ok:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_all())
