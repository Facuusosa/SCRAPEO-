import os
import asyncio
import logging
from typing import Optional
from core.http_client import AsyncHttpClient

logger = logging.getLogger("notifier")

class TelegramNotifier:
    """
    Sistema de notificaciones para Telegram.
    Permite enviar alertas de oportunidades confirmadas a canales VIP.
    """
    
    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        self.token = token or os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")
        self.client = AsyncHttpClient()
        
    async def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Envía un mensaje de texto simple."""
        if not self.token or not self.chat_id:
            logger.warning("⚠️ Telegram Notifier no configurado (falta TOKEN o CHAT_ID)")
            return False
            
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False
        }
        
        try:
            resp = await self.client.post(url, json=payload)
            if resp.status_code == 200:
                logger.info("✅ Alerta enviada a Telegram")
                return True
            else:
                logger.error(f"❌ Error enviando a Telegram: {resp.status_code} - {resp.text}")
                return False
        except Exception as e:
            logger.error(f"💥 Error en TelegramNotifier: {e}")
            return False

    async def send_opportunity(self, opp) -> bool:
        """
        Envía una alerta formateada de una oportunidad de Odiseo.
        'opp' debe ser una instancia de OdiseoOpportunity o un dict similar.
        """
        # Formatear el mensaje
        # Si es un objeto (dataclass)
        if hasattr(opp, "name"):
            name = opp.name
            price = opp.current_price
            gap = opp.gap_teorico
            margin = opp.margen_odiseo
            url = opp.url
            store = "Frávega" # Hardcoded por ahora o derivado
        else:
            name = opp.get("name", "Producto")
            price = opp.get("current_price", 0)
            gap = opp.get("gap_teorico", 0)
            margin = opp.get("margen_odiseo", 0)
            url = opp.get("url", "#")
            store = opp.get("store", "Tienda")

        msg = (
            f"🚀 <b>¡OPORTUNIDAD CONFIRMADA!</b>\n\n"
            f"📦 <b>{name}</b>\n"
            f"🏪 Tienda: {store}\n\n"
            f"💰 Precio: <b>${price:,.0f}</b>\n"
            f"📉 Gap: {gap:.1f}%\n"
            f"💸 <b>Margen Neto: {margin:.1f}%</b>\n\n"
            f"✅ Stock Validado (Real-time)\n"
            f"🔗 <a href='{url}'>VER PRODUCTO EN TIENDA</a>\n\n"
            f"🛰 <i>Enviado por Odiseo Bot v2.0</i>"
        ).replace(",", ".") # Formato AR: $1.234
        
        return await self.send_message(msg)
