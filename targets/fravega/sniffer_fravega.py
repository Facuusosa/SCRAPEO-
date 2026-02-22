"""
🕷️ Sniffer Frávega — Scraper con curl_cffi + Arquitectura Core

Refactorizado para usar:
- core.HttpClient (curl_cffi con impersonación Chrome + Circuit Breaker + Retry)
- core.BaseSniffer (clase abstracta con Template Method)
- core.Database (SQLite wrapper con batch operations)

Uso:
    python targets/fravega/sniffer_fravega.py
"""

import json
import os
import sys
import logging
from datetime import datetime
from typing import Optional

# Agregar el root del proyecto al path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from core.http_client import HttpClient, WAFBlockedError, CircuitBreaker
from core.base_sniffer import BaseSniffer, Product, Glitch

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("fravega")


# ============================================================================
# GLITCH DETECTION — Lógica de Élite (migrada del original)
# ============================================================================

def detect_price_glitch_fast(current_price, previous_price, list_price):
    """
    Función de Élite para detectar errores de carga (Glitches).
    Retorna (es_glitch, razon)
    """
    if current_price <= 0:
        return True, "Precio Inválido (0 o menor)"

    if list_price and current_price > list_price * 1.5:
        return True, "Precio Inflado Sospechoso"

    if previous_price and previous_price > 0:
        drop_percent = ((previous_price - current_price) / previous_price) * 100
        if drop_percent > 85:
            return True, f"Glitch probable: Caída del {drop_percent:.1f}%"

        increase_percent = ((current_price - previous_price) / previous_price) * 100
        if increase_percent > 400:
            return True, f"Aumento masivo sospechoso: {increase_percent:.1f}%"

    if current_price < 500 and list_price and list_price > 50000:
        return True, "Precio ridículamente bajo respecto a lista"

    return False, "Sano"


# ============================================================================
# FRAVEGA SNIFFER — Hereda de BaseSniffer
# ============================================================================

class FravegaSniffer(BaseSniffer):
    """
    Scraper de Frávega usando curl_cffi con impersonación Chrome.
    
    Cambios vs versión anterior:
    - curl_cffi en vez de requests (bypass WAF)
    - Session con cookies (simula navegación real)
    - Circuit Breaker (no bombardea si la API cae)
    - Retry con exponential backoff (nativo de curl_cffi)
    """
    
    TARGET_NAME = "fravega"
    BASE_URL = "https://www.fravega.com"
    API_URL = "https://www.fravega.com/api/v1"
    
    GRAPHQL_QUERY = """
    query listProducts($size: PositiveInt!, $offset: Int, $sorting: [SortOption!], $filtering: ItemFilteringInputType) {
      items(filtering: $filtering) {
        total
        results(
          size: $size
          buckets: [{sorting: $sorting, offset: $offset}]
        ) {
          id
          title
          slug
          brand { name }
          images
          skus {
            results {
              code
              images
              pricing {
                salePrice
                listPrice
                discount
              }
              stock {
                availability
                labels
              }
            }
          }
        }
      }
    }
    """
    
    def __init__(self, db_path: Optional[str] = None):
        # DB en el mismo directorio que el script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        default_db = os.path.join(script_dir, "fravega_monitor.db")
        super().__init__(db_path=db_path or default_db)
        
        # Cliente HTTP con curl_cffi
        self.client = HttpClient(
            impersonate="chrome",
            retry_count=3,
            retry_delay=0.5,
            circuit_breaker=CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=120,
            ),
            extra_headers={
                "Referer": "https://www.fravega.com/",
            },
        )
        
        # Primer request al home para obtener cookies
        self._warm_session()
        
        # DB legacy (mantenemos la estructura original por compatibilidad)
        self._init_legacy_db()
    
    def _warm_session(self) -> None:
        """Visitar homepage para obtener cookies (simular navegación real)."""
        try:
            r = self.client.get(self.BASE_URL)
            self.logger.info(f"🌐 Session calentada — Homepage: {r.status_code}")
        except Exception as e:
            self.logger.warning(f"⚠️ No se pudo calentar session: {e}")
    
    def _init_legacy_db(self) -> None:
        """Crear tablas de la DB original (compatibilidad)."""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    title TEXT,  -- Legacy
                    brand TEXT,
                    brand_name TEXT, -- Legacy
                    category TEXT,
                    last_price REAL,
                    list_price REAL,
                    lowest_price REAL,
                    discount_pct REAL DEFAULT 0,
                    url TEXT,
                    slug TEXT, -- Legacy
                    image_url TEXT,
                    source TEXT DEFAULT 'fravega',
                    last_seen DATETIME
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT,
                    old_price REAL,
                    new_price REAL,
                    timestamp DATETIME
                )
            """)
    
    # --- Implementación de métodos abstractos de BaseSniffer ---
    
    def fetch_products(self, category: str, size: int = 50, **kwargs) -> list[dict]:
        """
        Fetch productos via GraphQL API de Frávega.
        USA curl_cffi con impersonación Chrome → bypass WAF.
        """
        sorting = kwargs.get("sorting", "TOTAL_SALES_IN_LAST_30_DAYS")
        
        variables = {
            "size": size,
            "offset": 0,
            "sorting": sorting,
            "filtering": {
                "categories": [category],
                "active": True,
                "salesChannels": ["fravega-ecommerce"],
            },
        }
        
        try:
            response = self.client.post(
                self.API_URL,
                json={"query": self.GRAPHQL_QUERY, "variables": variables},
            )
            
            data = response.json()
            
            if "data" in data and data["data"].get("items"):
                items = data["data"]["items"]
                total = items.get("total", 0)
                results = items.get("results", [])
                self.logger.info(f"  📦 {category}: {len(results)}/{total} productos")
                return results
            else:
                self.logger.warning(f"  ⚠️ Estructura inesperada para {category}")
                if "errors" in data:
                    for err in data["errors"]:
                        self.logger.error(f"  GraphQL Error: {err.get('message', '?')}")
                return []
                
        except WAFBlockedError:
            self.logger.error(f"  🚫 WAF BLOCK en {category} — 403 Forbidden")
            return []
        except Exception as e:
            self.logger.error(f"  💥 Error fetching {category}: {e}")
            return []
    
    def parse_product(self, raw: dict) -> Product:
        """Convertir producto raw de Frávega API → Product normalizado."""
        pid = raw.get("id", "")
        title = raw.get("title", "Sin Título")
        slug = raw.get("slug", "")
        brand_name = raw.get("brand", {}).get("name", "Genérico") if isinstance(raw.get("brand"), dict) else "Genérico"
        
        # SKU data
        skus_data = raw.get("skus", {})
        skus_list = skus_data.get("results", []) if isinstance(skus_data, dict) else []
        
        current_price = 0.0
        list_price = 0.0
        discount_pct = 0.0
        sku_code = ""
        in_stock = False
        image_url = ""
        
        if skus_list and isinstance(skus_list, list) and len(skus_list) > 0:
            first_sku = skus_list[0]
            sku_code = first_sku.get("code", "")
            
            # Pricing
            pricing = first_sku.get("pricing", [])
            if isinstance(pricing, list) and len(pricing) > 0:
                price_data = pricing[0]
                current_price = float(price_data.get("salePrice", 0) or 0)
                list_price = float(price_data.get("listPrice", 0) or 0)
                discount_pct = float(price_data.get("discount", 0) or 0)
            elif isinstance(pricing, dict):
                current_price = float(pricing.get("salePrice", 0) or 0)
                list_price = float(pricing.get("listPrice", 0) or 0)
                discount_pct = float(pricing.get("discount", 0) or 0)
            
            # Stock
            stock_data = first_sku.get("stock")
            if isinstance(stock_data, dict):
                in_stock = bool(stock_data.get("availability", False))
            
            # Image (SKU level first, then product level)
            # La API devuelve solo hashes (ej: "abc123.jpg")
            # La URL real es: https://images.fravega.com/f300/{hash}
            IMG_BASE = "https://images.fravega.com/f300/"
            images = first_sku.get("images", [])
            if images and isinstance(images, list) and len(images) > 0:
                img_hash = images[0] if isinstance(images[0], str) else ""
            else:
                prod_images = raw.get("images", [])
                if prod_images and isinstance(prod_images, list) and len(prod_images) > 0:
                    img_hash = prod_images[0] if isinstance(prod_images[0], str) else ""
                else:
                    img_hash = ""
            
            # Construir URL completa si es solo un hash
            if img_hash and not img_hash.startswith("http"):
                image_url = f"{IMG_BASE}{img_hash}"
            else:
                image_url = img_hash
        
        return Product(
            id=pid,
            name=title,
            brand=brand_name,
            current_price=current_price,
            list_price=list_price,
            discount_pct=discount_pct,
            url=f"{self.BASE_URL}/p/{slug}" if slug else "",
            image_url=image_url,
            source=self.TARGET_NAME,
            in_stock=in_stock,
            raw_data={"sku_code": sku_code, "slug": slug},
        )
    
    def detect_glitch(self, product: Product, previous_price: float = 0.0) -> Optional[Glitch]:
        """
        Usar la detección de glitches original de élite + la del BaseSniffer.
        """
        # Primero la detección legacy
        is_glitch, reason = detect_price_glitch_fast(
            product.current_price,
            previous_price,
            product.list_price,
        )
        
        if is_glitch:
            severity = "critical" if "ridículo" in reason.lower() else "high"
            return Glitch(
                product=product,
                reason=reason,
                severity=severity,
                previous_price=previous_price,
            )
        
        # Fallback al detector del BaseSniffer
        return super().detect_glitch(product, previous_price)
    
    def save_products(self, products: list[Product]) -> None:
        """Guardar en la DB legacy (compatible con el esquema original)."""
        import sqlite3
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for p in products:
                if not p.in_stock:
                    continue
                
                # Verificar precio anterior
                cursor.execute("SELECT last_price, lowest_price FROM products WHERE id = ?", (p.id,))
                row = cursor.fetchone()
                
                if row:
                    last_price, lowest_price = row
                    
                    # Detectar caída
                    if p.current_price < last_price:
                        diff = last_price - p.current_price
                        percent = (diff / last_price) * 100
                        
                        glitch = self.detect_glitch(p, last_price)
                        if glitch:
                            tag = "⚡ BUG/GLITCH"
                        else:
                            tag = "🔥 ALERT"
                        
                        self.logger.info(
                            f"[{tag}] {p.name[:50]} bajó ${diff:,.0f} ({percent:.1f}%) "
                            f"→ ${p.current_price:,.0f}"
                        )
                        
                        # Guardar alerta
                        conn.execute(
                            "INSERT INTO alerts (product_id, old_price, new_price, timestamp) "
                            "VALUES (?, ?, ?, ?)",
                            (p.id, last_price, p.current_price, datetime.now()),
                        )
                    
                    # Update
                    new_lowest = min(p.current_price, (lowest_price or p.current_price))
                    cursor.execute("""
                        UPDATE products 
                        SET last_price = ?, list_price = ?, lowest_price = ?, last_seen = ?,
                            category = ?, image_url = ?, brand = ?, brand_name = ?, 
                            name = ?, title = ?, url = ?, slug = ?, discount_pct = ?
                        WHERE id = ?
                    """, (
                        p.current_price, p.list_price, new_lowest, datetime.now(),
                        p.category, p.image_url, p.brand, p.brand,
                        p.name, p.name, p.url, p.raw_data.get("slug", ""), p.discount_pct,
                        p.id,
                    ))
                else:
                    # Insert nuevo
                    cursor.execute("""
                        INSERT INTO products (id, name, title, brand, brand_name, category, 
                                            last_price, list_price, lowest_price, discount_pct,
                                            url, slug, image_url, source, last_seen)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        p.id, p.name, p.name, p.brand, p.brand, p.category,
                        p.current_price, p.list_price, p.current_price, p.discount_pct,
                        p.url, p.raw_data.get("slug", ""), p.image_url, "fravega", datetime.now(),
                    ))
    
    def on_glitch_found(self, glitch: Glitch) -> None:
        """Log de glitches detectados."""
        self.logger.warning(
            f"🚨 GLITCH [{glitch.severity.upper()}] {glitch.product.name[:50]} "
            f"→ ${glitch.product.current_price:,.0f} — {glitch.reason}"
        )


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Cargar categorías
    data_dir = os.path.join(PROJECT_ROOT, "data")
    json_path = os.path.join(data_dir, "clean_categories.json")
    
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            raw_categories = json.load(f)
        target_categories = [c.strip("/") for c in raw_categories if c.strip("/")]
        logger.info(f"📦 Loaded {len(target_categories)} categories from {json_path}")
    else:
        logger.info(f"[!] {json_path} not found. Using defaults.")
        target_categories = [
            "celulares-y-smartphones/celulares-y-smartphones",
            "audio/auriculares",
            "tv-y-video/tv",
            "gaming/consolas",
            "computacion/notebooks",
        ]
    
    sniffer = FravegaSniffer()
    
    # Un solo ciclo para testing, o run_forever para producción
    import argparse
    parser = argparse.ArgumentParser(description="Frávega Price Sniffer")
    parser.add_argument("--daemon", action="store_true", help="Correr en loop infinito")
    parser.add_argument("--interval", type=int, default=60, help="Segundos entre ciclos")
    parser.add_argument("--categories", nargs="+", help="Categorías específicas")
    args = parser.parse_args()
    
    cats = args.categories or target_categories
    
    if args.daemon:
        sniffer.run_forever(cats, interval=args.interval)
    else:
        results = sniffer.run_cycle(cats)
        
        # Resumen
        total_products = sum(r.products_found for r in results)
        total_glitches = sum(r.glitches_found for r in results)
        total_errors = sum(len(r.errors) for r in results)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 RESUMEN: {total_products} productos, "
                     f"{total_glitches} glitches, {total_errors} errores")
        logger.info(f"{'='*60}")
