import asyncio
import os
import sys

# Agregar root al path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from core.http_client import AsyncHttpClient

async def get_bot_updates(token):
    client = AsyncHttpClient()
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    
    print(f"\n🔍 Buscando actualizaciones para el bot...")
    print(f"👉 Por favor, envía un mensaje a tu bot en Telegram ahora.")
    
    try:
        resp = await client.get(url)
        if resp.status_code == 200:
            data = resp.json()
            if not data.get("result"):
                print("❌ No se encontraron mensajes nuevos. Asegúrate de haberle escrito al bot.")
                return
            
            last_chat = data["result"][-1]["message"]["chat"]
            chat_id = last_chat["id"]
            username = last_chat.get("username", "N/A")
            
            print(f"\n✅ ¡CONEXIÓN EXITOSA!")
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"👤 Usuario: @{username}")
            print(f"🆔 CHAT_ID: {chat_id}")
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"\nConfigura estas variables en tu entorno:")
            print(f"export TELEGRAM_BOT_TOKEN={token}")
            print(f"export TELEGRAM_CHAT_ID={chat_id}")
        else:
            print(f"❌ Error al consultar la API: {resp.status_code}")
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    token = input("Introduce el TOKEN de tu bot de Telegram: ").strip()
    if token:
        asyncio.run(get_bot_updates(token))
    else:
        print("Token no válido.")
