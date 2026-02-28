"""
🕷️ SNIFFER FRÁVEGA V2 — Con Stock Validation + Margen Odiseo

NUEVO PIPELINE:
[GraphQL API] → [Filtro Gap >= 18%] → [Calc Margen Odiseo] 
    → [Stock Validator (Playwright)] → [Confirmado] → [ALERTA]

Features:
- curl_cffi + Circuit Breaker (bypass WAF)
- Playwright solo para confirmación final (eficiente)
- Margen Odiseo = (Gap - 5%) >= 10% (costo reales)
- DB con histórico para análisis
- Alertas SOLO en oportunidades confirmadas

Uso:
    python targets/fravega/sniffer_fravega_v2.py --daemon
"""

import json
import os
import sys
import logging
import asyncio
import random
from datetime import datetime
from typing import Optional, Tuple
from dataclasses import dataclass

# Agregar root al path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from core.http_client import HttpClient, WAFBlockedError, CircuitBreaker
from core.base_sniffer import BaseSniffer, Product, Glitch
from core.notifier import TelegramNotifier

# Playwright para stock validation
try:
    from playwright.async_api import async_playwright
except ImportError:
    print("⚠️ Playwright not installed. Run: pip install playwright")
    sys.exit(1)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("fravega-v2")


# ============================================================================
# TIPOS
# ============================================================================

@dataclass
class OdiseoOpportunity:
    """Oportunidad de arbitrage validada."""
    product_id: str
    name: str
    current_price: float
    list_price: float
    gap_teorico: float  # %
    margen_odiseo: float  # % (Gap - 5%)
    stock_validado: bool
    timestamp: str
    url: str
    tiempo_validacion_ms: int


# ============================================================================
# VALIDADOR DE STOCK + MARGEN
# ============================================================================

class StockValidator:
    """
    Valida stock real vía Playwright con Pool de Navegadores y Semáforo.
    Optimizado para no saturar la RAM.
    """
    
    def __init__(self, proxy_url: Optional[str] = None):
        self.proxy_url = proxy_url
        self.semaphore = asyncio.Semaphore(3)  # Máximo 3 validaciones concurrentes
        self.playwright = None
        self.browser = None
    
    async def start(self):
        """Inicializa el browser si no existe."""
        if not self.browser:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ]
            )
            logger.info("📡 Browser Pool inicializado")

    async def stop(self):
        """Cierra el pool."""
        if self.browser:
            await self.browser.close()
            await self.playwright.stop()
            self.browser = None
            logger.info("🛑 Browser Pool apagado")
    
    @staticmethod
    def _calcular_margen_odiseo(gap_teorico: float) -> float:
        return gap_teorico - 5.0
    
    @staticmethod
    async def _random_human_delay(min_sec: float = 1.0, max_sec: float = 5.0):
        await asyncio.sleep(random.uniform(min_sec, max_sec))
    
    async def validar_stock_add_to_cart(self, product_url: str, sku_id: str) -> Tuple[bool, str, int]:
        """
        Validar stock con protección de concurrencia.
        """
        async with self.semaphore:
            await self.start()
            inicio = datetime.now()
            
            # Contexto aislado por cada validación
            context = await self.browser.new_context(
                proxy={"server": self.proxy_url} if self.proxy_url else None,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )
            
            page = await context.new_page()
            try:
                # 1. Navegar con timeout agresivo
                await page.goto(product_url, wait_until="domcontentloaded", timeout=25000)
                
                # 2. Simular lectura
                await page.evaluate(f"window.scrollBy(0, {random.randint(100, 400)})")
                await self._random_human_delay(1, 3)
                
                # 3. Buscar botón (Filtro por data-testid o texto)
                add_btn = await page.query_selector("button[data-testid='add-to-cart'], button:has-text('Agregar')")
                
                if not add_btn:
                    return False, "boton_no_encontrado", int((datetime.now() - inicio).total_seconds() * 1000)
                
                if await add_btn.is_disabled():
                    return False, "stock_agotado", int((datetime.now() - inicio).total_seconds() * 1000)
                
                # 4. Click y confirmación
                await add_btn.click()
                await asyncio.sleep(2.5)
                
                # 5. Verificar carrito
                cart_count = await page.query_selector("span[data-testid='cart-count'], .cart-qty, .cart-count")
                in_cart = False
                if cart_count:
                    text = await cart_count.inner_text()
                    in_cart = "0" not in text and text.strip() != ""
                else:
                    # Fallback por elementos de item
                    items = await page.query_selector_all("div[data-testid='cart-item'], .cart-product")
                    in_cart = len(items) > 0
                
                razon = "validado_ok" if in_cart else "no_se_agrego"
                return in_cart, razon, int((datetime.now() - inicio).total_seconds() * 1000)
                
            except Exception as e:
                return False, f"error: {str(e)[:40]}", int((datetime.now() - inicio).total_seconds() * 1000)
            finally:
                await page.close()
                await context.close()


# ============================================================================
# FRAVEGA SNIFFER V2
# ============================================================================

class FravegaSnifferV2(BaseSniffer):
    """
    Scraper mejorado con validación de stock + margen odiseo.
    
    Pipeline:
    1. GraphQL fetch (rápido, curl_cffi)
    2. Calcular gap teórico
    3. Si gap >= 18% → candidato
    4. Calcular margen odiseo (gap - 5%)
    5. Si margen >= 10% → ir a Playwright
    6. Playwright valida stock real
    7. Si OK → ALERTA confirmada
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
    
    # Precio de "mercado mínimo" (asumimos que Cetrogar/Megatone son competidores base)
    # En producción, esto vendría de un agregador de precios
    MARKET_MIN_PRICES = {
        "samsung": 800_000,  # Notebooks Samsung típicamente
        "lenovo": 750_000,
        "acer": 700_000,
        "hp": 800_000,
    }
    
    def __init__(self, db_path: Optional[str] = None, proxy_url: Optional[str] = None):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        default_db = os.path.join(script_dir, "fravega_monitor_v2.db")
        super().__init__(db_path=db_path or default_db)
        
        # Client HTTP con curl_cffi
        self.client = HttpClient(
            impersonate="chrome",
            retry_count=3,
            retry_delay=0.5,
            circuit_breaker=CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=120,
            ),
            extra_headers={"Referer": "https://www.fravega.com/"},
        )
        
        # Stock validator con Playwright
        self.validator = StockValidator(proxy_url=proxy_url)
        
        # Telegram Notifier
        self.notifier = TelegramNotifier()
        
        # Estadísticas
        self.stats = {
            "candidatos": 0,
            "validados": 0,
            "rechazados_margen": 0,
            "rechazados_stock": 0,
        }
        
        self._warm_session()
        self._init_legacy_db()
    
    def _warm_session(self) -> None:
        """Calentar sesión con cookies."""
        try:
            r = self.client.get(self.BASE_URL)
            self.logger.info(f"🌐 Session calentada — Homepage: {r.status_code}")
        except Exception as e:
            self.logger.warning(f"⚠️ No se pudo calentar session: {e}")
    
    def _init_legacy_db(self) -> None:
        """Crear tablas."""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    brand TEXT,
                    current_price REAL,
                    list_price REAL,
                    lowest_price REAL,
                    discount_pct REAL DEFAULT 0,
                    url TEXT,
                    slug TEXT,
                    image_url TEXT,
                    source TEXT DEFAULT 'fravega',
                    last_seen DATETIME
                );
                
                CREATE TABLE IF NOT EXISTS opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT,
                    product_name TEXT,
                    current_price REAL,
                    gap_teorico REAL,
                    margen_odiseo REAL,
                    stock_validado INTEGER,
                    tiempo_validacion_ms INTEGER,
                    confirmed_at DATETIME
                );
                
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT,
                    alert_type TEXT,  -- 'oportunidad', 'glitch'
                    message TEXT,
                    timestamp DATETIME
                );
            """)
    
    def _get_market_min_price(self, brand: str, category: str) -> float:
        """
        Obtener el precio mínimo de mercado asumido.
        En producción: consultaría un agregador de precios real.
        """
        brand_lower = brand.lower()
        
        # Lookup por marca
        for brand_key, price in self.MARKET_MIN_PRICES.items():
            if brand_key in brand_lower:
                return price
        
        # Default por categoría (si la tuviéramos)
        return 750_000  # Asumiendo notebooks como default
    
    def _calcular_gap_y_margen(self, current_price: float, brand: str, category: str) -> Tuple[float, float]:
        """
        Calcular gap teórico y margen odiseo.
        
        Gap = (Precio_Min_Mercado - Precio_Fravega) / Precio_Fravega * 100
        Margen_Odiseo = Gap - 5%
        """
        market_min = self._get_market_min_price(brand, category)
        
        if current_price <= 0:
            return 0.0, 0.0
        
        gap = ((market_min - current_price) / current_price) * 100
        margen = gap - 5.0
        
        return gap, margen
    
    async def procesar_candidato(self, product: Product) -> Optional[OdiseoOpportunity]:
        """
        Procesar un candidato (gap >= 18%) a través del pipeline completo.
        
        Pipeline:
        1. Calcular gap + margen
        2. Filtro margen (>= 10%)
        3. Stock validation (Playwright)
        4. Return oportunidad confirmada o None
        """
        
        gap, margen = self._calcular_gap_y_margen(
            product.current_price, 
            product.brand, 
            product.category
        )
        
        # Re-verificar gap (por si acaso)
        if gap < 18:
            self.logger.debug(f"⏭️ {product.name[:40]} — Gap {gap:.1f}% < 18%, descartado")
            return None
        
        self.stats["candidatos"] += 1
        self.logger.info(f"🎯 CANDIDATO: {product.name[:40]} | Gap: {gap:.1f}% | Margen: {margen:.1f}%")
        
        # Filtro 1: Margen Odiseo >= 10%
        if margen < 10:
            self.logger.warning(
                f"  ❌ Margen Odiseo {margen:.1f}% < 10% → DESCARTADO"
            )
            self.stats["rechazados_margen"] += 1
            return None
        
        self.logger.info(f"  ✅ Margen Odiseo OK ({margen:.1f}%) → Validando stock...")
        
        # Filtro 2: Validar stock con Playwright
        try:
            stock_ok, razon, tiempo_ms = await self.validator.validar_stock_add_to_cart(
                product.url, 
                product.raw_data.get("sku_code", "?")
            )
            
            if not stock_ok:
                self.logger.warning(
                    f"  ❌ Stock validation failed: {razon} → DESCARTADO"
                )
                self.stats["rechazados_stock"] += 1
                return None
            
            self.logger.info(f"  ✅ Stock VALIDADO ({tiempo_ms}ms)")
            
        except Exception as e:
            self.logger.error(f"  💥 Error en stock validation: {e}")
            self.stats["rechazados_stock"] += 1
            return None
        
        # ✅ OPORTUNIDAD CONFIRMADA
        self.stats["validados"] += 1
        
        opp = OdiseoOpportunity(
            product_id=product.id,
            name=product.name,
            current_price=product.current_price,
            list_price=product.list_price,
            gap_teorico=gap,
            margen_odiseo=margen,
            stock_validado=True,
            timestamp=datetime.now().isoformat(),
            url=product.url,
            tiempo_validacion_ms=tiempo_ms,
        )
        
        self.logger.info(f"\n🚀 ╔════════════════════════════════════════")
        self.logger.info(f"🚀 ║ OPORTUNIDAD ODISEO CONFIRMADA")
        self.logger.info(f"🚀 ║ Producto: {opp.name[:50]}")
        self.logger.info(f"🚀 ║ Precio Fravega: ${opp.current_price:,.0f}")
        self.logger.info(f"🚀 ║ Gap: {opp.gap_teorico:.1f}% | Margen: {opp.margen_odiseo:.1f}%")
        self.logger.info(f"🚀 ║ Stock: ✅ VALIDADO | Tiempo: {tiempo_ms}ms")
        self.logger.info(f"🚀 ╚════════════════════════════════════════\n")
        
        return opp
    
    def fetch_products(self, category: str, size: int = 50, **kwargs) -> list[dict]:
        """Fetch via GraphQL (igual al v1)."""
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
                results = items.get("results", [])
                self.logger.info(f"  📦 {category}: {len(results)} productos")
                return results
            else:
                self.logger.warning(f"  ⚠️ Estructura inesperada para {category}")
                return []
                
        except WAFBlockedError:
            self.logger.error(f"  🚫 WAF BLOCK — 403 Forbidden")
            return []
        except Exception as e:
            self.logger.error(f"  💥 Error fetching: {e}")
            return []
    
    def parse_product(self, raw: dict) -> Product:
        """Parse producto raw → Product (igual al v1)."""
        pid = raw.get("id", "")
        title = raw.get("title", "Sin Título")
        slug = raw.get("slug", "")
        brand_name = raw.get("brand", {}).get("name", "Genérico") if isinstance(raw.get("brand"), dict) else "Genérico"
        
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
            
            stock_data = first_sku.get("stock")
            if isinstance(stock_data, dict):
                in_stock = bool(stock_data.get("availability", False))
            
            images = first_sku.get("images", [])
            if images and isinstance(images, list) and len(images) > 0:
                img_hash = images[0]
            else:
                prod_images = raw.get("images", [])
                if prod_images and isinstance(prod_images, list) and len(prod_images) > 0:
                    img_hash = prod_images[0]
                else:
                    img_hash = ""
            
            IMG_BASE = "https://images.fravega.com/f300/"
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
    
    def save_products(self, products: list[Product]) -> None:
        """Guardar productos normales en DB (para Radar/Market data)."""
        import sqlite3
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            for p in products:
                if p.current_price <= 0:
                    continue
                
                conn.execute("""
                    INSERT OR REPLACE INTO products (
                        id, name, brand, current_price, list_price, 
                        discount_pct, url, slug, image_url, source, last_seen
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    p.id, p.name, p.brand, p.current_price, p.list_price,
                    p.discount_pct, p.url, p.raw_data.get("slug", ""), 
                    p.image_url, p.source, now
                ))
            conn.commit()
        self.logger.info(f"💾 {len(products)} productos guardados en {self.db_path}")
    
    def save_opportunity(self, opp: OdiseoOpportunity) -> None:
        """Guardar oportunidad validada en DB."""
        db_url = os.environ.get("DATABASE_URL")
        
        if db_url:
            # Postgres (Producción)
            try:
                import psycopg2
                with psycopg2.connect(db_url) as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO opportunities 
                            (product_id, name, price, gap_teorico, margen_odiseo, 
                             stock_validado, store, url, confirmed_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            opp.product_id, opp.name, opp.current_price, opp.gap_teorico,
                            opp.margen_odiseo, int(opp.stock_validado), "Frávega", opp.url,
                            opp.timestamp,
                        ))
                self.logger.info("✅ Oportunidad guardada en Postgres")
                return
            except Exception as e:
                self.logger.error(f"❌ Error guardando en Postgres: {e}")
        
        # Fallback a SQLite (Local)
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("""
                INSERT INTO opportunities 
                (product_id, product_name, current_price, gap_teorico, margen_odiseo, 
                 stock_validado, tiempo_validacion_ms, confirmed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                opp.product_id, opp.name, opp.current_price, opp.gap_teorico,
                opp.margen_odiseo, int(opp.stock_validado), opp.tiempo_validacion_ms,
                opp.timestamp,
            ))
            
            conn.execute("""
                INSERT INTO alerts (product_id, alert_type, message, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                opp.product_id, "oportunidad",
                f"Margen {opp.margen_odiseo:.1f}% | Stock validado",
                datetime.now(),
            ))


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Orquestador async del sniffer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Frávega Sniffer V2 — Con Stock Validation")
    parser.add_argument("--proxy", type=str, help="Proxy URL (ej: http://user:pass@proxy.com:80)")
    parser.add_argument("--daemon", action="store_true", help="Correr en loop infinito")
    parser.add_argument("--interval", type=int, default=300, help="Segundos entre ciclos")
    args = parser.parse_args()
    
    # Cargar categorías
    data_dir = os.path.join(PROJECT_ROOT, "data")
    json_path = os.path.join(data_dir, "clean_categories.json")
    
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            raw_categories = json.load(f)
        target_categories = [c.strip("/") for c in raw_categories if c.strip("/")]
        logger.info(f"📦 Loaded {len(target_categories)} categorías")
    else:
        target_categories = [
            "computacion/notebooks",
            "celulares-y-smartphones/celulares-y-smartphones",
        ]
    
    sniffer = FravegaSnifferV2(proxy_url=args.proxy)
    
    cycle = 0
    while True:
        cycle += 1
        if args.daemon:
            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 CICLO #{cycle} — {datetime.now().strftime('%H:%M:%S')}")
            logger.info(f"{'='*60}")

        # Procesar todas las categorías
        for category in target_categories:
            logger.info(f"\n{'='*60}")
            logger.info(f"🔍 Escaneando: {category}")
            logger.info(f"{'='*60}")
            
            # Fetch
            raw_products = sniffer.fetch_products(category, size=20)
            
            # Parse
            products = [sniffer.parse_product(p) for p in raw_products]
            products = [p for p in products if p.in_stock and p.current_price > 0]
            
            logger.info(f"✅ {len(products)} productos válidos")
            
            # Guardar en DB para Radar (Capa de Inteligencia)
            sniffer.save_products(products)
            
            # Filtrar candidatos (gap >= 18%)
            for product in products:
                gap, _ = sniffer._calcular_gap_y_margen(product.current_price, product.brand, category)
                
                if gap >= 18:
                    # Procesar async
                    opp = await sniffer.procesar_candidato(product)
                    
                    if opp:
                        # Guardar en DB
                        sniffer.save_opportunity(opp)
                        
                        # 🚀 ENVIAR ALERTA TELEGRAM
                        await sniffer.notifier.send_opportunity(opp)
        
        # Resumen
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 RESUMEN CICLO #{cycle}")
        logger.info(f"{'='*60}")
        logger.info(f"Candidatos detectados: {sniffer.stats['candidatos']}")
        logger.info(f"Oportunidades validadas: {sniffer.stats['validados']}")
        logger.info(f"Rechazados por margen: {sniffer.stats['rechazados_margen']}")
        logger.info(f"Rechazados por stock: {sniffer.stats['rechazados_stock']}")
        logger.info(f"{'='*60}\n")

        if not args.daemon:
            break
        
        logger.info(f"⏳ Esperando {args.interval}s para el siguiente ciclo...")
        await asyncio.sleep(args.interval)


if __name__ == "__main__":
    asyncio.run(main())
