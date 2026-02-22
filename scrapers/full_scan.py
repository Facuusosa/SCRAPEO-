"""
Full Scrape + Analysis
Scrapea TODAS las categorias y luego muestra las mejores oportunidades.
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from targets.fravega.sniffer_fravega import FravegaSniffer
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("SCAN")

# Cargar categorias
json_path = os.path.join("data", "clean_categories.json")
if os.path.exists(json_path):
    with open(json_path, "r") as f:
        raw = json.load(f)
    cats = [c.strip("/") for c in raw if c.strip("/")]
else:
    cats = [
        "celulares-y-smartphones/celulares-y-smartphones",
        "audio/auriculares",
        "tv-y-video/tv",
        "gaming/consolas",
        "computacion/notebooks",
    ]

log.info(f"=== FULL SCRAPE: {len(cats)} categorias ===")

sniffer = FravegaSniffer()

total_products = 0
total_glitches = 0
total_errors = 0
all_products = []
start_time = time.time()

for i, cat in enumerate(cats):
    log.info(f"[{i+1}/{len(cats)}] {cat}")
    try:
        results = sniffer.run_cycle([cat])
        r = results[0]
        total_products += r.products_found
        total_glitches += r.glitches_found
        total_errors += len(r.errors)
        all_products.extend(r.products)

        if r.errors:
            for e in r.errors:
                log.warning(f"  ERROR: {e}")
    except Exception as e:
        log.error(f"  FATAL: {e}")
        total_errors += 1

    # Rate limiting: 1s entre categorias
    if i < len(cats) - 1:
        time.sleep(1)

elapsed = time.time() - start_time

log.info(f"\n{'='*60}")
log.info(f"SCRAPE COMPLETO en {elapsed:.0f}s ({elapsed/60:.1f} min)")
log.info(f"Productos: {total_products}")
log.info(f"Glitches: {total_glitches}")
log.info(f"Errores: {total_errors}")
log.info(f"{'='*60}")

# === ANALISIS ===
if all_products:
    # Filtrar productos con precio valido
    valid = [p for p in all_products if p.current_price > 0 and p.in_stock]
    log.info(f"\nProductos validos (con precio y stock): {len(valid)}")

    # Top descuentos
    with_discount = [p for p in valid if p.list_price > 0 and p.current_price < p.list_price]
    with_discount.sort(key=lambda p: p.calculated_discount, reverse=True)

    log.info(f"\n{'='*60}")
    log.info(f"TOP 20 MAYORES DESCUENTOS")
    log.info(f"{'='*60}")
    for i, p in enumerate(with_discount[:20], 1):
        margin = p.list_price - p.current_price
        log.info(
            f"{i:2d}. {p.name[:50]}\n"
            f"    Precio: ${p.current_price:>12,.0f} | "
            f"Lista: ${p.list_price:>12,.0f} | "
            f"Desc: {p.calculated_discount}% | "
            f"Ahorro: ${margin:,.0f}"
        )

    # Top mas baratos
    cheapest = sorted(valid, key=lambda p: p.current_price)
    log.info(f"\n{'='*60}")
    log.info(f"TOP 20 MAS BARATOS (todos)")
    log.info(f"{'='*60}")
    for i, p in enumerate(cheapest[:20], 1):
        log.info(
            f"{i:2d}. {p.name[:50]}\n"
            f"    ${p.current_price:>12,.0f} | {p.category}"
        )

    # Margen de reventa (comprar al precio actual, vender al precio lista)
    resale = [p for p in with_discount if p.calculated_discount >= 15]
    resale.sort(key=lambda p: p.list_price - p.current_price, reverse=True)

    log.info(f"\n{'='*60}")
    log.info(f"TOP 20 OPORTUNIDADES DE REVENTA (>=15% margen)")
    log.info(f"{'='*60}")
    for i, p in enumerate(resale[:20], 1):
        profit = p.list_price - p.current_price
        margin_pct = p.calculated_discount
        log.info(
            f"{i:2d}. {p.name[:50]}\n"
            f"    Comprar: ${p.current_price:>12,.0f} | "
            f"Vender: ~${p.list_price:>12,.0f} | "
            f"Ganancia: ${profit:>10,.0f} ({margin_pct}%)"
        )

    # Stats por categoria
    cat_stats = {}
    for p in valid:
        cat = p.category
        if cat not in cat_stats:
            cat_stats[cat] = {"count": 0, "avg_discount": 0, "products": []}
        cat_stats[cat]["count"] += 1
        cat_stats[cat]["products"].append(p)

    for cat in cat_stats:
        prods = cat_stats[cat]["products"]
        discounts = [p.calculated_discount for p in prods if p.calculated_discount > 0]
        cat_stats[cat]["avg_discount"] = sum(discounts) / len(discounts) if discounts else 0

    top_cats = sorted(cat_stats.items(), key=lambda x: x[1]["avg_discount"], reverse=True)

    log.info(f"\n{'='*60}")
    log.info(f"TOP 10 CATEGORIAS POR DESCUENTO PROMEDIO")
    log.info(f"{'='*60}")
    for cat, stats in top_cats[:10]:
        log.info(f"  {cat}: {stats['count']} prods, avg desc: {stats['avg_discount']:.1f}%")
