"""
Sniffer Cetrogar - Scraper Magento 2 GraphQL

Stack: Magento 2 con GraphQL abierto
API: POST /graphql con query products(search, pageSize, currentPage)

Descubierto en recon del 2026-02-21:
  - GraphQL abierto sin autenticacion
  - Datos completos: nombre, sku, precio, lista, descuento, stock, imagen, categorias
  - Paginacion via currentPage/pageSize (max 50 por pagina)

Ejemplo:
    from targets.cetrogar.sniffer_cetrogar import CetrogarSniffer
    
    sniffer = CetrogarSniffer()
    results = sniffer.run_cycle(["celulares", "notebooks", "smart-tv"])
"""

from __future__ import annotations

import logging
import sqlite3
import json
from datetime import datetime
from typing import Optional

from core.base_sniffer import BaseSniffer, Product, Glitch
from core.http_client import HttpClient

logger = logging.getLogger(__name__)


# ============================================================================
# QUERY GRAPHQL PARA MAGENTO 2
# ============================================================================

PRODUCTS_QUERY = """
query GetProducts($search: String!, $pageSize: Int!, $currentPage: Int!) {
  products(search: $search, pageSize: $pageSize, currentPage: $currentPage) {
    items {
      name
      sku
      url_key
      small_image { url }
      price_range {
        minimum_price {
          regular_price { value currency }
          final_price { value currency }
          discount { amount_off percent_off }
        }
      }
      stock_status
    }
    total_count
    page_info { current_page page_size total_pages }
  }
}
"""

# Busqueda por categoria URL (sin search text)
CATEGORY_QUERY = """
query GetCategoryProducts($urlKey: String!, $pageSize: Int!, $currentPage: Int!) {
  products(
    filter: { category_url_key: { eq: $urlKey } }
    pageSize: $pageSize
    currentPage: $currentPage
  ) {
    items {
      name
      sku
      url_key
      small_image { url }
      price_range {
        minimum_price {
          regular_price { value currency }
          final_price { value currency }
          discount { amount_off percent_off }
        }
      }
      stock_status
    }
    total_count
    page_info { current_page page_size total_pages }
  }
}
"""


# ============================================================================
# CATEGORIAS CETROGAR - url_keys para filtrar
# ============================================================================

CETROGAR_CATEGORIES = {
    # Tecnologia
    "celulares": {"search": "celular", "url_key": "smartphones"},
    "notebooks": {"search": "notebook", "url_key": "notebooks"},
    "tablets": {"search": "tablet", "url_key": "tablets"},
    "smartwatches": {"search": "smartwatch", "url_key": None},
    "consolas": {"search": "consola", "url_key": None},
    
    # Audio/TV
    "smart-tv": {"search": "smart tv", "url_key": "televisores"},
    "audio": {"search": "parlante auricular", "url_key": None},
    "soundbar": {"search": "soundbar barra sonido", "url_key": None},
    
    # Electrodomesticos
    "aires": {"search": "aire acondicionado", "url_key": "aires-acondicionados"},
    "heladeras": {"search": "heladera", "url_key": "heladeras"},
    "lavarropas": {"search": "lavarropas", "url_key": "lavarropas"},
    "cocinas": {"search": "cocina", "url_key": "cocinas"},
    "microondas": {"search": "microondas", "url_key": "microondas"},
    "cafeteras": {"search": "cafetera", "url_key": None},
    "freidoras": {"search": "freidora", "url_key": None},
    "aspiradoras": {"search": "aspiradora", "url_key": None},
    "freezers": {"search": "freezer", "url_key": "freezers"},
}


# ============================================================================
# CETROGAR SNIFFER
# ============================================================================

class CetrogarSniffer(BaseSniffer):
    """
    Scraper de Cetrogar usando Magento 2 GraphQL.
    
    La API GraphQL de Magento permite:
    - Buscar por texto (search)
    - Filtrar por categoria (category_url_key)
    - Paginar con currentPage/pageSize (max 50)
    - Obtener precio, lista, descuento, stock, imagen
    """
    
    TARGET_NAME = "cetrogar"
    BASE_URL = "https://www.cetrogar.com.ar"
    API_URL = "https://www.cetrogar.com.ar/graphql"
    
    PAGE_SIZE = 50  # Magento max
    
    def __init__(self, db_path: Optional[str] = None):
        super().__init__(db_path or "cetrogar_monitor.db")
        
        self.client = HttpClient(
            stealth_mode=True,
            rotate_browser=True,
            retry_count=3,
            delay_range=(1.0, 3.0),
        )
        
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
                sku TEXT,
                stock_status TEXT DEFAULT 'IN_STOCK',
                first_seen TEXT,
                last_seen TEXT,
                price_history TEXT DEFAULT '[]',
                source TEXT DEFAULT 'cetrogar'
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
        self.logger.info(f"DB inicializada: {self.db_path}")
    
    def fetch_products(self, category: str, size: int = 500, **kwargs) -> list[dict]:
        """
        Fetch via Magento 2 GraphQL.
        Usa search term ya que el filtro por category_url_key no esta disponible en este server.
        """
        cat_config = CETROGAR_CATEGORIES.get(category, {"search": category, "url_key": None})
        search_term = cat_config["search"]
        
        # Warm session
        self.client.warm_session(self.BASE_URL)
        
        all_items = []
        current_page = 1
        # Calcular cuantas paginas necesitamos para llegar al size
        max_pages = (size + self.PAGE_SIZE - 1) // self.PAGE_SIZE
        
        while current_page <= max_pages:
            try:
                variables = {
                    "search": search_term,
                    "pageSize": self.PAGE_SIZE,
                    "currentPage": current_page,
                }
                payload = {"query": PRODUCTS_QUERY, "variables": variables}
                
                response = self.client.post(
                    self.API_URL,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Store": "default",
                    },
                )
                
                if response.status_code != 200:
                    self.logger.warning(f"   Status {response.status_code} en pagina {current_page}")
                    break
                
                data = response.json()
                
                # Verificar errores GraphQL
                if "errors" in data:
                    msg = data["errors"][0].get("message", "Unknown GraphQL error")
                    self.logger.warning(f"   GraphQL error: {msg[:80]}")
                    if "products" not in data.get("data", {}):
                        break
                
                products_data = data.get("data", {}).get("products", {})
                if not products_data:
                    break
                    
                items = products_data.get("items", [])
                page_info = products_data.get("page_info", {})
                total_count = products_data.get("total_count", 0)
                
                if not items:
                    break
                
                all_items.extend(items)
                total_pages = page_info.get("total_pages", 1)
                
                self.logger.info(
                    f"   Cetrogar {category}: pag {current_page}/{total_pages}, "
                    f"+{len(items)} (total: {len(all_items)}/{total_count})"
                )
                
                if current_page >= total_pages or len(all_items) >= size:
                    break
                
                current_page += 1
                
            except Exception as e:
                self.logger.error(f"   Error fetch {category} pag {current_page}: {e}")
                break
        
        return all_items[:size]
    
    def parse_product(self, raw: dict) -> Product:
        """Convertir producto Magento GraphQL -> Product normalizado."""
        sku = raw.get("sku", "")
        name = raw.get("name", "Sin nombre")
        url_key = raw.get("url_key", "")
        url = f"{self.BASE_URL}/{url_key}.html" if url_key else ""
        
        # Imagen
        small_img = raw.get("small_image", {})
        image_url = small_img.get("url", "") if small_img else ""
        
        # Precios
        price_range = raw.get("price_range", {})
        min_price = price_range.get("minimum_price", {})
        
        regular = min_price.get("regular_price", {})
        final = min_price.get("final_price", {})
        discount_info = min_price.get("discount", {})
        
        current_price = float(final.get("value", 0))
        list_price = float(regular.get("value", 0))
        discount_pct = float(discount_info.get("percent_off", 0))
        
        # Stock
        stock_status = raw.get("stock_status", "IN_STOCK")
        in_stock = stock_status == "IN_STOCK"
        
        # Marca (extraer del nombre si es posible)
        brand = ""
        known_brands = ["Samsung", "LG", "Sony", "Philips", "TCL", "Motorola", "Apple",
                       "Xiaomi", "BGH", "Philco", "Noblex", "Whirlpool", "Drean", "Electrolux",
                       "Atma", "Midea", "Hisense", "HP", "Lenovo", "Dell", "Asus", "Acer",
                       "JBL", "Logitech", "Enova", "Skyworth", "Kanji"]
        name_lower = name.lower()
        for b in known_brands:
            if b.lower() in name_lower:
                brand = b
                break
        
        return Product(
            id=sku,
            name=name,
            brand=brand,
            current_price=current_price,
            list_price=list_price,
            discount_pct=discount_pct,
            url=url,
            image_url=image_url,
            source=self.TARGET_NAME,
            in_stock=in_stock,
            raw_data={"sku": sku, "stock_status": stock_status},
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
                existing = conn.execute(
                    "SELECT last_price, price_history FROM products WHERE id = ?",
                    (p.id,)
                ).fetchone()
                
                sku = p.raw_data.get("sku", "")
                stock_status = p.raw_data.get("stock_status", "IN_STOCK")
                
                if existing:
                    old_price = existing[0]
                    history = existing[1] or "[]"
                    
                    if abs(old_price - p.current_price) > 0.01:
                        hist = json.loads(history)
                        hist.append({"price": p.current_price, "date": now})
                        hist = hist[-100:]
                        history = json.dumps(hist)
                        
                        if old_price > 0:
                            change_pct = ((p.current_price - old_price) / old_price) * 100
                            if change_pct < -5:
                                conn.execute("""
                                    INSERT INTO alerts (product_id, product_name, alert_type,
                                        old_price, new_price, discount_pct, timestamp, details)
                                    VALUES (?, ?, 'price_drop', ?, ?, ?, ?, ?)
                                """, (p.id, p.name, old_price, p.current_price,
                                      abs(change_pct), now, f"Bajo {abs(change_pct):.1f}%"))
                    
                    conn.execute("""
                        UPDATE products SET
                            name=?, brand=?, category=?, last_price=?, list_price=?,
                            discount_pct=?, url=?, image_url=?, sku=?, stock_status=?,
                            last_seen=?, price_history=?
                        WHERE id=?
                    """, (p.name, p.brand, p.category, p.current_price, p.list_price,
                          p.discount_pct, p.url, p.image_url, sku, stock_status,
                          now, history, p.id))
                else:
                    history = json.dumps([{"price": p.current_price, "date": now}])
                    conn.execute("""
                        INSERT INTO products (id, name, brand, category, last_price, list_price,
                            discount_pct, url, image_url, sku, stock_status, first_seen, last_seen,
                            price_history, source)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'cetrogar')
                    """, (p.id, p.name, p.brand, p.category, p.current_price, p.list_price,
                          p.discount_pct, p.url, p.image_url, sku, stock_status,
                          now, now, history))
                
                saved += 1
            except Exception as e:
                self.logger.error(f"   Error guardando {p.name[:30]}: {e}")
        
        conn.commit()
        conn.close()
        self.logger.info(f"   {saved}/{len(products)} productos guardados en {self.db_path}")
    
    def close(self):
        """Cerrar recursos."""
        self.client.close()
