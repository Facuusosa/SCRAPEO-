"""
🕷️ Sniffer Tienda Newsan — Ninja HTML Scraper

Stack: Magento 2 (con WAF agresivo)
Método: HTML Parsing + Cookie Bypass (clonando sesión de usuario real)

Descubierto en recon del 2026-02-21:
  - Las APIs REST/GQL están bloqueadas (401/500).
  - El HTML contiene todos los datos: nombre, precio final, precio lista e imagen.
  - Al clonar las cookies de una sesión real (PHPSESSID), el WAF nos deja pasar.
"""

from __future__ import annotations

import logging
import sqlite3
import re
import html
from datetime import datetime
from typing import Optional

from core.base_sniffer import BaseSniffer, Product, Glitch
from core.http_client import HttpClient

logger = logging.getLogger(__name__)

# ============================================================================
# CATEGORÍAS NEWSAN
# ============================================================================

NEWSAN_CATEGORIES = {
    "celulares": "celulares",
    "smart-tv": "televisores",
    "notebooks": "notebooks",
    "aires": "aires-acondicionados",
    "heladeras": "heladeras",
    "lavarropas": "lavarropas",
    "pequenos-electro": "pequenos-electrodomesticos",
    "audio": "audio",
}

# ============================================================================
# NEWSAN SNIFFER
# ============================================================================

class NewsanSniffer(BaseSniffer):
    """
    Scraper de Tienda Newsan usando extraccion de datos del HTML.
    
    Bypass: Usa cookies de sesion real capturadas via DevTools.
    """
    
    TARGET_NAME = "newsan"
    BASE_URL = "https://www.tiendanewsan.com.ar"
    SEARCH_URL = "https://www.tiendanewsan.com.ar/catalogsearch/result/?q="
    
    def __init__(self, db_path: Optional[str] = None):
        super().__init__(db_path or "newsan_monitor.db")
        
        self.client = HttpClient(stealth_mode=True)
        
        # --- CREDENCIALES NINJA (Actualizadas al 2026-02-21 22:55) ---
        self.cookies = {
            'form_key': 'KcKkjvKkcvCSGsRQ',
            'PHPSESSID': 'df1b30b1b0468994aa259539e31f341c',
        }
        
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'referer': 'https://tiendanewsan.com.ar/'
        }
        
        self._init_db()

    def _init_db(self):
        """Crear tablas si no existen."""
        import sqlite3
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
                source TEXT DEFAULT 'newsan',
                last_seen TEXT
            )
        """)
        conn.commit()
        conn.close()

    def fetch_products(self, category: str, size: int = 50, **kwargs) -> list[dict]:
        """
        Fetch productos con paginación ninja.
        """
        keyword = NEWSAN_CATEGORIES.get(category, category)
        all_found = []
        
        # Newsan usa ?p=X o &p=X para paginar en sus resultados de búsqueda
        for page in range(1, 10): 
            url = f"{self.SEARCH_URL}{keyword}&p={page}"
            
            self.logger.info(f"📡 Navegando Newsan Search {category} P{page}: {url}")
            
            try:
                response = self.client.get(url, headers=self.headers, cookies=self.cookies)
                if response.status_code != 200: break
                
                html_content = response.text
                
                # Bloques de producto
                items_raw = re.findall(r'<div class=\"product-item-info\"(.*?)</div>\s*</div>', html_content, re.DOTALL)
                if not items_raw:
                    items_raw = re.findall(r'<li[^>]*class=\"[^\"]*product-item[^\"]*\"[^>]*>(.*?)</li>', html_content, re.DOTALL)
                
                if not items_raw: break
                
                page_prods = []
                for item in items_raw:
                    try:
                        name_match = re.search(r'product-item-link[^>]+>([^<]+)</a>', item)
                        if not name_match: continue
                        name = html.unescape(name_match.group(1).strip())
                        
                        price_matches = re.findall(r'<span class=\"price\">\$&nbsp;([0-9\.]+)</span>', item)
                        if not price_matches:
                            price_matches = re.findall(r'<span class=\"price\">\$([0-9\.]+)</span>', item)
                        if not price_matches:
                            price_matches = re.findall(r'data-price-amount=\"([0-9\.]+)\"', item)
                        
                        if not price_matches: continue
                        
                        current_price = float(price_matches[0].replace(".", "")) if "." in price_matches[0] else float(price_matches[0])
                        list_price = float(price_matches[1].replace(".", "")) if len(price_matches) > 1 and "." in price_matches[1] else (float(price_matches[1]) if len(price_matches) > 1 else current_price)
                        
                        url_match = re.search(r'href=\"(https://www.tiendanewsan.com.ar/[^\"]+)\"', item)
                        prod_url = url_match.group(1) if url_match else ""
                        
                        img_match = re.search(r'src=\"(https://www.tiendanewsan.com.ar/[^\"]+)\"', item)
                        image_url = img_match.group(1) if img_match else ""
                        
                        id_match = re.search(r'data-product-id=\"(\d+)\"', item)
                        product_id = id_match.group(1) if id_match else prod_url.split("/")[-1]

                        if current_price > 1000:
                            page_prods.append({
                                "id": product_id, "name": name, "price": current_price,
                                "list_price": list_price, "url": prod_url, "image_url": image_url
                            })
                    except: continue
                
                if not page_prods: break
                all_found.extend(page_prods)
                self.logger.info(f"   → P{page}: {len(page_prods)} productos")
                
                if len(all_found) >= size: break
                
            except Exception as e:
                self.logger.error(f"Error en P{page}: {e}")
                break
                
        return all_found
        return all_found

    def parse_product(self, raw: dict) -> Product:
        """Convertir dict de fetch -> Product normalizado."""
        
        # Calcular % descuento
        current = raw["price"]
        list_p = raw["list_price"]
        discount = 0.0
        if list_p > current and list_p > 0:
            discount = round((1 - current / list_p) * 100, 1)
        
        # Detectar marca del nombre
        brand = ""
        known_brands = ["Atma", "Philco", "Siam", "Noblex", "Whirlpool", "Motorola", "Samsung", "LG"]
        name_upper = raw["name"].upper()
        for b in known_brands:
            if b.upper() in name_upper:
                brand = b
                break

        return Product(
            id=raw["id"],
            name=raw["name"],
            brand=brand,
            current_price=current,
            list_price=list_p,
            discount_pct=discount,
            url=raw["url"],
            image_url=raw["image_url"],
            source=self.TARGET_NAME,
            in_stock=True # Si aparece en la lista de busqueda, asumimos stock
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
