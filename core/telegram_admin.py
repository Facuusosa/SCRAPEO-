import os
import logging
from typing import Optional
from core.http_client import AsyncHttpClient

logger = logging.getLogger("telegram-admin")

class TelegramAdmin:
    """
    Gestión administrativa del bot de Telegram.
    Permite crear links de invitación temporales para nuevos suscriptores.
    """
    
    def __init__(self, token: Optional[str] = None, main_chat_id: Optional[str] = None):
        self.token = token or os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = main_chat_id or os.environ.get("TELEGRAM_CHAT_ID")
        self.client = AsyncHttpClient()

    async def create_invite_link(self, name: str, expire_hours: int = 24) -> Optional[str]:
        """
        Crea un link de invitación único para un suscriptor.
        """
        if not self.token or not self.chat_id:
            return None
            
        url = f"https://api.telegram.org/bot{self.token}/createChatInviteLink"
        payload = {
            "chat_id": self.chat_id,
            "name": f"VIP Access: {name}",
            "member_limit": 1, # Un solo uso
            "expire_date": int(os.time.time() + (expire_hours * 3600)) if hasattr(os, 'time') else None 
        }
        
        # Use simple time approach
        import time
        payload["expire_date"] = int(time.time() + (expire_hours * 3600))

        try:
            resp = await self.client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["result"]["invite_link"]
            return None
        except Exception as e:
            logger.error(f"Error creating invite link: {e}")
            return None
