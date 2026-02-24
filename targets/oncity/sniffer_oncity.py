"""
🕷️ Sniffer On City (ex-Musimundo) — Scraper VTEX REST API

Stack: VTEX Commerce Platform (mismo que Frávega)
API: REST /api/catalog_system/pub/products/search
     REST /api/catalog_system/pub/category/tree/3

Descubierto en recon del 2026-02-21:
  - Status 200 en todos los endpoints
  - Sin WAF agresivo
  - Datos completos: nombre, marca, precio, lista, stock, imagen, EAN

Ejemplo:
    from targets.oncity.sniffer_oncity import OnCitySniffer
    
    sniffer = OnCitySniffer()
    results = sniffer.run_cycle(["celulares", "notebooks", "smart-tv"])
"""

from __future__ import annotations
import os
import sys
import logging
import sqlite3
import time
import random
from datetime import datetime
from typing import Any, Optional

# Agregar el root del proyecto al path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from core.base_sniffer import BaseSniffer, Product, Glitch
from core.http_client import HttpClient

logger = logging.getLogger(__name__)


# ============================================================================
# CATEGORÍAS PRIORITARIAS — Las que importan para arbitraje
# ============================================================================

# Mapeo: nombre_corto → path VTEX para buscar
ONCITY_CATEGORIES = {
    # Tecnología (prioridad alta)
    "celulares": "tecnologia/celulares",
    "notebooks": "tecnologia/informatica/notebooks",
    "tablets": "tecnologia/informatica/tablets",
    "smartwatches": "tecnologia/smartwatches",
    "consolas": "tecnologia/gaming/consolas",
    "gaming": "tecnologia/gaming",
    "informatica": "tecnologia/informatica",
    
    # Audio, TV y Video
    "smart-tv": "audio-tv-y-video/televisores",
    "audio": "audio-tv-y-video/audio",
    "soundbar": "audio-tv-y-video/audio/soundbar",
    
    # Electrodomésticos (paths corregidos 2026-02-21)
    "aires": "electrodomesticos/climatizacion/aires-acondicionados",
    "heladeras": "electrodomesticos/heladeras-y-freezers/heladeras",
    "freezers": "electrodomesticos/heladeras-y-freezers/freezers",
    "lavarropas": "electrodomesticos/lavado-y-secado/lavarropas",
    "lavasecarropas": "electrodomesticos/lavado-y-secado/lavasecarropas",
    "cocinas": "electrodomesticos/de-cocina/cocinas",
    "microondas": "electrodomesticos/de-cocina/microondas",
    "cafeteras": "electrodomesticos/pequenos-electro-de-cocina/cafeteras",
    "freidoras": "electrodomesticos/pequenos-electro-de-cocina/freidoras",
    "aspiradoras": "electrodomesticos/pequenos-electro-de-hogar/aspiradoras-y-barredoras",
    
    # Generales
    "ofertas": "",  # Sin categoría = todos los productos
}


# ============================================================================
# ON CITY SNIFFER — Hereda de BaseSniffer
# ============================================================================

class OnCitySniffer(BaseSniffer):
    """
    Scraper de On City (ex-Musimundo) usando VTEX REST API.
    
    VTEX expone una API REST pública de búsqueda de productos:
    - /api/catalog_system/pub/products/search/{category}
    - Paginación: _from=0&_to=49 (max 50 por página)
    - Header "resources" en la respuesta indica total de resultados
    
    Features:
    - Scraping completo de catálogo con paginación
    - Datos ricos: precio, lista, stock, EAN, marca, imagen
    - Stealth mode integrado via HttpClient
    """
    
    TARGET_NAME = "oncity"
    BASE_URL = "https://www.oncity.com"
    API_URL = "https://www.oncity.com/api/catalog_system/pub/products/search"
    CATEGORIES_URL = "https://www.oncity.com/api/catalog_system/pub/category/tree/3"
    
    # VTEX pagina de a 50 productos máximo
    PAGE_SIZE = 50
    
    def __init__(self, db_path: Optional[str] = None):
        super().__init__(db_path or "oncity_monitor.db")
        
        # HttpClient con stealth activado
        self.client = HttpClient(
            stealth_mode=True,
            rotate_browser=True,
            retry_count=3,
            delay_range=(1.0, 3.0),  # Un poco más conservador
        )
        
        # Inicializar DB
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
                ean TEXT,
                stock INTEGER DEFAULT 0,
                first_seen TEXT,
                last_seen TEXT,
                price_history TEXT DEFAULT '[]',
                source TEXT DEFAULT 'oncity'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT,
                product_name TEXT,
                alert_type TEXT,
                old_price REAL,
                new_price REAL,
                discount_pct REAL,
                timestamp TEXT,
                details TEXT
            )
        """)
        conn.commit()
        conn.close()
        self.logger.info(f"💾 DB inicializada: {self.db_path}")
    
    # --- Implementación de métodos abstractos ---
    
    def fetch_products(self, category: str, size: int = 200, **kwargs) -> list[dict]:
        """
        Fetch productos via VTEX REST API con paginación.
        
        La API VTEX retorna máximo 50 productos por request.
        Paginamos automáticamente hasta obtener `size` productos.
        
        Args:
            category: Nombre corto de categoría (e.g., "celulares")
            size: Cantidad máxima de productos a obtener
        """
        # Resolver path de categoría
        cat_path = ONCITY_CATEGORIES.get(category, category)
        
        # Warm session
        self.client.warm_session(self.BASE_URL)
        
        all_products = []
        offset = 0
        
        while offset < size:
            end = min(offset + self.PAGE_SIZE - 1, size - 1)
            
            # Construir URL
            if cat_path:
                url = f"{self.API_URL}/{cat_path}?_from={offset}&_to={end}"
            else:
                url = f"{self.API_URL}?_from={offset}&_to={end}"
            
            try:
                response = self.client.get(url, headers={"Accept": "application/json"})
                
                if response.status_code in (200, 206):
                    products = response.json()
                    
                    if not products or not isinstance(products, list):
                        break
                    
                    all_products.extend(products)
                    self.logger.info(
                        f"   📦 {category}: página {offset//self.PAGE_SIZE + 1}, "
                        f"+{len(products)} productos (total: {len(all_products)})"
                    )
                    
                    # Si devolvió menos de PAGE_SIZE, no hay más
                    if len(products) < self.PAGE_SIZE:
                        break
                    
                    offset += self.PAGE_SIZE
                else:
                    self.logger.warning(f"   ⚠️ Status {response.status_code} para {cat_path}")
                    break
                    
            except Exception as e:
                self.logger.error(f"   ❌ Error fetch {category} offset {offset}: {e}")
                break
        
        return all_products
    
    def parse_product(self, raw: dict) -> Product:
        """
        Convertir producto VTEX raw → Product normalizado.
        
        Estructura VTEX:
            raw["productName"] → nombre
            raw["brand"] → marca
            raw["items"][0]["sellers"][0]["commertialOffer"]["Price"] → precio
            raw["items"][0]["sellers"][0]["commertialOffer"]["ListPrice"] → precio lista
            raw["items"][0]["images"][0]["imageUrl"] → imagen
            raw["items"][0]["sellers"][0]["commertialOffer"]["AvailableQuantity"] → stock
        """
        # Datos básicos
        product_id = str(raw.get("productId", ""))
        name = raw.get("productName", "Sin nombre")
        brand = raw.get("brand", "")
        link = raw.get("link", "")
        
        # Categoría
        categories = raw.get("categories", [])
        category = categories[0] if categories else ""
        
        # SKU principal (primer item)
        items = raw.get("items", [])
        first_sku = items[0] if items else {}
        
        # Imagen
        images = first_sku.get("images", [])
        image_url = images[0].get("imageUrl", "") if images else ""
        
        # EAN
        ean = first_sku.get("ean", "")
        
        # Precio (del primer seller)
        sellers = first_sku.get("sellers", [])
        first_seller = sellers[0] if sellers else {}
        offer = first_seller.get("commertialOffer", {})
        
        current_price = float(offer.get("Price", 0))
        list_price = float(offer.get("ListPrice", 0))
        stock = int(offer.get("AvailableQuantity", 0))
        
        # Calcular descuento
        discount_pct = 0.0
        if list_price > 0 and current_price > 0 and current_price < list_price:
            discount_pct = round((1 - current_price / list_price) * 100, 1)
        
        return Product(
            id=product_id,
            name=name,
            brand=brand,
            current_price=current_price,
            list_price=list_price,
            discount_pct=discount_pct,
            url=link,
            image_url=image_url,
            category=category,
            source=self.TARGET_NAME,
            in_stock=stock > 0,
            raw_data={"ean": ean, "stock": stock},
        )
    
    def save_products(self, products: list[Product]) -> None:
        """Guardar productos en SQLite."""
        conn = sqlite3.connect(self.db_path)
        now = datetime.now().isoformat()
        saved = 0
        
        for p in products:
            if p.current_price <= 0:
                continue
            
            try:
                # Verificar si existe
                existing = conn.execute(
                    "SELECT last_price, price_history FROM products WHERE id = ?",
                    (p.id,)
                ).fetchone()
                
                ean = p.raw_data.get("ean", "")
                stock = p.raw_data.get("stock", 0)
                
                if existing:
                    old_price = existing[0]
                    history = existing[1] or "[]"
                    
                    # Agregar al historial si cambió el precio
                    if abs(old_price - p.current_price) > 0.01:
                        import json
                        hist = json.loads(history)
                        hist.append({"price": p.current_price, "date": now})
                        # Mantener últimos 100 registros
                        hist = hist[-100:]
                        history = json.dumps(hist)
                        
                        # Registrar alerta si bajó más de 5%
                        if old_price > 0:
                            change_pct = ((p.current_price - old_price) / old_price) * 100
                            if change_pct < -5:
                                conn.execute("""
                                    INSERT INTO alerts (product_id, product_name, alert_type,
                                        old_price, new_price, discount_pct, timestamp, details)
                                    VALUES (?, ?, 'price_drop', ?, ?, ?, ?, ?)
                                """, (p.id, p.name, old_price, p.current_price, 
                                      abs(change_pct), now, f"Bajó {abs(change_pct):.1f}%"))
                    
                    conn.execute("""
                        UPDATE products SET
                            name=?, brand=?, category=?, last_price=?, list_price=?,
                            discount_pct=?, url=?, image_url=?, ean=?, stock=?,
                            last_seen=?, price_history=?
                        WHERE id=?
                    """, (p.name, p.brand, p.category, p.current_price, p.list_price,
                          p.discount_pct, p.url, p.image_url, ean, stock,
                          now, history, p.id))
                else:
                    import json
                    history = json.dumps([{"price": p.current_price, "date": now}])
                    
                    conn.execute("""
                        INSERT INTO products (id, name, brand, category, last_price, list_price,
                            discount_pct, url, image_url, ean, stock, first_seen, last_seen,
                            price_history, source)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'oncity')
                    """, (p.id, p.name, p.brand, p.category, p.current_price, p.list_price,
                          p.discount_pct, p.url, p.image_url, ean, stock,
                          now, now, history))
                
                saved += 1
            except Exception as e:
                self.logger.error(f"   ❌ Error guardando {p.name[:30]}: {e}")
        
        conn.commit()
        conn.close()
        self.logger.info(f"   💾 {saved}/{len(products)} productos guardados en {self.db_path}")
    
    def get_all_categories(self) -> list[dict]:
        """Obtener árbol completo de categorías de On City."""
        self.client.warm_session(self.BASE_URL)
        return self.client.get_json(self.CATEGORIES_URL)
    
    def close(self):
        """Cerrar recursos."""
        self.client.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="OnCity Price Sniffer")
    parser.add_argument("--daemon", action="store_true", help="Correr en loop infinito")
    parser.add_argument("--interval", type=int, default=120, help="Segundos entre ciclos")
    parser.add_argument("--categories", nargs="+", help="Categorías específicas")
    args = parser.parse_args()
    
    cats = args.categories or list(ONCITY_CATEGORIES.keys())
    sniffer = OnCitySniffer()
    
    if args.daemon:
        sniffer.run_forever(cats, interval=args.interval)
    else:
        sniffer.run_cycle(cats)
