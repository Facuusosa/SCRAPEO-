"""
🕷️ Sniffer Megatone — Scraper via Doofinder API

Stack: Motor de búsqueda Doofinder externo
API: GET https://us1-search.doofinder.com/6/.../_search

Descubierto en recon del 2026-02-21:
  - Megatone delega su búsqueda a Doofinder.
  - La API es pública si se envían los referers correctos.
  - Devuelve JSON enriquecido con precios, stock y marcas.
  - Soporta hasta 100 resultados por request.
"""

import os
import sys
import logging
import sqlite3
import json
from datetime import datetime
from typing import Optional

# Agregar el root del proyecto al path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from core.base_sniffer import BaseSniffer, Product, Glitch
from core.http_client import HttpClient

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURACIÓN DOOFINDER (Capturada del cURL del usuario)
# ============================================================================

DOOFINDER_HASH = "7d78864dfd68192d967ce98f7af00970"
DOOFINDER_URL = f"https://us1-search.doofinder.com/6/{DOOFINDER_HASH}/_search"

# Mapeo de categorías a términos de búsqueda
MEGATONE_CATEGORIES = {
    "celulares": "celular",
    "notebooks": "notebook",
    "tablets": "tablet",
    "smart-tv": "smart tv",
    "aires": "aire acondicionado",
    "heladeras": "heladera",
    "lavarropas": "lavarropas",
    "cocinas": "cocina",
    "audio": "parlante",
    "consolas": "consola",
}

# ============================================================================
# MEGATONE SNIFFER
# ============================================================================

class MegatoneSniffer(BaseSniffer):
    """
    Scraper de Megatone usando la API de búsqueda de Doofinder.
    """
    
    TARGET_NAME = "megatone"
    BASE_URL = "https://www.megatone.net"
    
    def __init__(self, db_path: Optional[str] = None):
        super().__init__(db_path or "megatone_monitor.db")
        
        self.client = HttpClient(stealth_mode=True)
        
        # Headers necesarios para que Doofinder no nos rebote
        self.headers = {
            'accept': '*/*',
            'accept-language': 'es-ES,es;q=0.9',
            'origin': 'https://www.megatone.net',
            'referer': 'https://www.megatone.net/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'
        }
        
        self._init_db()

    def _init_db(self):
        """Crear tablas si no existen."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT,
                brand TEXT,
                category TEXT,
                last_price REAL,
                list_price REAL,
                discount_pct REAL DEFAULT 0,
                url TEXT,
                image_url TEXT,
                source TEXT DEFAULT 'megatone',
                last_seen TEXT
            )
        """)
        conn.commit()
        conn.close()

    def fetch_products(self, category: str, size: int = 200, **kwargs) -> list[dict]:
        """
        Fetch productos desde Doofinder.
        """
        query_term = MEGATONE_CATEGORIES.get(category, category)
        all_products = []
        
        # Doofinder permite paginar con 'page'
        page = 1
        rpp = 100 # Results per page (max recomendado)
        
        while len(all_products) < size:
            url = f"{DOOFINDER_URL}?page={page}&rpp={rpp}&query={query_term}"
            self.logger.info(f"📡 Fetching Megatone via Doofinder (pag {page}): {query_term}")
            
            try:
                # No necesitamos warm_session para Doofinder ya que es externo
                response = self.client.get(url, headers=self.headers)
                
                if response.status_code != 200:
                    self.logger.error(f"❌ Error en Doofinder: Status {response.status_code}")
                    break
                
                data = response.json()
                results = data.get('results', [])
                
                if not results:
                    break
                
                all_products.extend(results)
                
                # Ver si hay más páginas (total es el total de items encontrados)
                total = data.get('total', 0)
                if len(all_products) >= total or len(results) < rpp:
                    break
                
                page += 1
                
            except Exception as e:
                self.logger.error(f"💥 Error en fetch Megatone: {e}")
                break
                
        return all_products[:size]

    def parse_product(self, raw: dict) -> Product:
        """Convertir JSON Doofinder -> Product normalizado."""
        
        # Precios
        current_price = float(raw.get('best_price', raw.get('sale_price', 0)))
        list_price = float(raw.get('price', current_price))
        
        # Calcular % descuento si no viene
        discount = float(raw.get('calculated_discount', 0.0))
        if discount == 0 and list_price > current_price and list_price > 0:
            discount = round((1 - current_price / list_price) * 100, 1)
        
        return Product(
            id=raw.get('id', raw.get('dfid', '')),
            name=raw.get('title', 'Sin nombre'),
            brand=raw.get('brand', ''),
            current_price=current_price,
            list_price=list_price,
            discount_pct=discount,
            url=raw.get('link', ''),
            image_url=raw.get('image_link', ''),
            source=self.TARGET_NAME,
            in_stock=(raw.get('availability', '').lower() == 'in stock')
        )

    def save_products(self, products: list[Product]) -> None:
        """Guardar en SQLite."""
        conn = sqlite3.connect(self.db_path)
        now = datetime.now().isoformat()
        for p in products:
            conn.execute("""
                INSERT OR REPLACE INTO products 
                (id, name, brand, category, last_price, list_price, discount_pct, url, image_url, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (p.id, p.name, p.brand, p.category, p.current_price, p.list_price, p.discount_pct, p.url, p.image_url, now))
        conn.commit()
        conn.close()

    def close(self):
        self.client.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Megatone Price Sniffer")
    parser.add_argument("--daemon", action="store_true", help="Correr en loop infinito")
    parser.add_argument("--interval", type=int, default=120, help="Segundos entre ciclos")
    parser.add_argument("--categories", nargs="+", help="Categorías específicas")
    args = parser.parse_args()
    
    cats = args.categories or list(MEGATONE_CATEGORIES.keys())
    sniffer = MegatoneSniffer()
    
    if args.daemon:
        sniffer.run_forever(cats, interval=args.interval)
    else:
        sniffer.run_cycle(cats)
