"""
🕷️ Sniffer Casa del Audio — HTML Scraper with Cookie Bypass

Stack: Magento 2
Método: HTML Parsing + Cookie Bypass (clonando sesión de usuario real)

Descubierto en recon del 2026-02-21:
  - APIs GraphQL/REST a veces bloqueadas o requieren tokens dinámicos.
  - El HTML contiene los datos de productos y precios en bloques estándar de Magento.
  - Usa cookies de sesión (PHPSESSID y form_key) para autenticar la navegación.
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
# CATEGORÍAS CASA DEL AUDIO
# ============================================================================

CASADELAUDIO_CATEGORIES = {
    "celulares": "tecnologia/celulares-y-accesorios.html",
    "smart-tv": "tv-y-audio/tv-y-video.html",
    "notebooks": "tecnologia/computacion.html",
    "aires": "climatizacion/aires-acondicionados.html",
    "heladeras": "electrodomesticos/heladeras-y-freezers.html",
    "lavarropas": "electrodomesticos/lavado-y-secado.html",
    "cocinas": "electrodomesticos/cocinas-y-hornos.html",
    "audio": "tv-y-audio/audio.html",
    "pequenos-electro": "electrodomesticos/pequenos-electrodomesticos.html",
}

# ============================================================================
# CASA DEL AUDIO SNIFFER
# ============================================================================

class CasaDelAudioSniffer(BaseSniffer):
    """
    Scraper de Casa del Audio usando extraccion de datos del HTML.
    """
    
    TARGET_NAME = "casadelaudio"
    BASE_URL = "https://casadelaudio.com"
    
    def __init__(self, db_path: Optional[str] = None):
        super().__init__(db_path or "casadelaudio_monitor.db")
        
        self.client = HttpClient(stealth_mode=True)
        
        # --- CREDENCIALES (Actualizadas al 2026-02-21 22:46) ---
        self.cookies = {
            'PHPSESSID': 'df1b30b1b0468994aa259539e31f341c',
            'form_key': 'a1StOBLpPQps8tKn',
        }
        
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'es-ES,es;q=0.9',
            'referer': 'https://casadelaudio.com/'
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
                source TEXT DEFAULT 'casadelaudio',
                last_seen TEXT
            )
        """)
        conn.commit()
        conn.close()

    def fetch_products(self, category: str, size: int = 24, **kwargs) -> list[dict]:
        """
        Fetch productos con paginación real.
        size en Casa del Audio suele ser fijo por página (24).
        """
        cat_suffix = CASADELAUDIO_CATEGORIES.get(category, f"catalogsearch/result/?q={category}")
        all_found = []
        
        # Iterar páginas hasta encontrar lo solicitado o quedarnos sin productos
        for page in range(1, 10): # Limite de 10 paginas por seguridad
            sep = "&" if "?" in cat_suffix else "?"
            url = f"{self.BASE_URL}/{cat_suffix}{sep}p={page}"
            
            self.logger.info(f"📡 Navegando Casa del Audio {category} P{page}: {url}")
            
            try:
                response = self.client.get(url, headers=self.headers, cookies=self.cookies)
                if response.status_code != 200: break
                
                html_content = response.text
                
                # Intentar encontrar el listado principal
                main_list_match = re.search(r'<div[^>]*class=\"[^\"]*products wrapper[^\"]*\">(.*?)<div[^>]*class=\"[^\"]*toolbar-bottom[^\"]*\"', html_content, re.DOTALL)
                cur_html = main_list_match.group(1) if main_list_match else html_content
                
                # Bloques de producto
                items_raw = re.findall(r'<li[^>]*class=\"[^\"]*product-item[^\"]*\"[^>]*>(.*?)</li>', cur_html, re.DOTALL)
                
                if not items_raw: break
                
                page_prods = []
                for item in items_raw:
                    try:
                        if 'product-item-details' not in item: continue
                        
                        name_match = re.search(r'product-item-link[^>]+>([^<]+)</a>', item)
                        if not name_match:
                            name_match = re.search(r'alt=\"([^\"]+)\" class=\"product-image-photo\"', item)
                        if not name_match: continue
                        name = html.unescape(name_match.group(1).strip())
                        
                        price_matches = re.findall(r'data-price-amount=\"([0-9\.]+)\"', item)
                        if not price_matches: continue
                        
                        current_price = float(price_matches[0])
                        list_price = float(price_matches[1]) if len(price_matches) > 1 else current_price
                        
                        url_match = re.search(r'href=\"(https://casadelaudio.com/[^\"]+)\"', item)
                        prod_url = url_match.group(1) if url_match else ""
                        
                        img_match = re.search(r'src=\"(https://casadelaudio.com/media/catalog/product/[^\"]+)\"', item)
                        image_url = img_match.group(1) if img_match else ""
                        
                        id_match = re.search(r'data-product-id=\"(\d+)\"', item)
                        product_id = id_match.group(1) if id_match else prod_url.split("/")[-1].replace(".html", "")

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

    def parse_product(self, raw: dict) -> Product:
        """Convertir dict de fetch -> Product normalizado."""
        
        current = raw["price"]
        list_p = raw["list_price"]
        discount = 0.0
        if list_p > current and list_p > 0:
            discount = round((1 - current / list_p) * 100, 1)
        
        # Detectar marca
        brand = ""
        known_brands = ["Samsung", "Motorola", "Oppo", "Philco", "Atma", "Noblex", "Whirlpool", "Drean", "LG", "Philips"]
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
            in_stock=True
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
