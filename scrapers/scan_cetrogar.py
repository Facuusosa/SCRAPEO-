"""Scan completo de Cetrogar."""
import sys, os
# Agregar el root del proyecto al path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

from targets.cetrogar.sniffer_cetrogar import CetrogarSniffer

sniffer = CetrogarSniffer()

categories = [
    'celulares', 'notebooks', 'tablets', 'smartwatches', 'consolas',
    'smart-tv', 'audio', 'soundbar',
    'aires', 'heladeras', 'lavarropas', 'cocinas', 'microondas',
    'cafeteras', 'freidoras', 'aspiradoras', 'freezers',
]

results = sniffer.run_cycle(categories, size=500)

lines = []
lines.append('='*60)
lines.append('SCAN CETROGAR - RESULTADOS')
lines.append('='*60)

total = 0
for r in results:
    total += r.products_found
    status = 'OK' if r.success else 'VACIO' if r.products_found == 0 else 'ERR'
    lines.append(f'  {r.category:20s} | {r.products_found:4d} prods | {r.glitches_found} glitches | {r.duration_seconds:.1f}s | {status}')

lines.append(f'\nTOTAL: {total} productos')

# Stats de DB
import sqlite3
conn = sqlite3.connect('cetrogar_monitor.db')
conn.row_factory = sqlite3.Row
stats = conn.execute("""
    SELECT COUNT(*) as total,
           COUNT(CASE WHEN discount_pct > 0 THEN 1 END) as con_desc,
           ROUND(AVG(CASE WHEN discount_pct > 0 THEN discount_pct END), 1) as avg_disc,
           ROUND(MAX(discount_pct), 1) as max_disc,
           COUNT(CASE WHEN discount_pct >= 30 THEN 1 END) as hot
    FROM products WHERE last_price > 0
""").fetchone()
lines.append(f'\nEN DB: {stats["total"]} prods | {stats["con_desc"]} con desc | avg: {stats["avg_disc"]}% | max: {stats["max_disc"]}% | 30%+: {stats["hot"]}')

# Top 10
lines.append('\nTOP 10 DESCUENTOS:')
top = conn.execute("""
    SELECT name, brand, last_price, list_price, discount_pct, url
    FROM products WHERE discount_pct > 0
    ORDER BY discount_pct DESC LIMIT 10
""").fetchall()
for i, p in enumerate(top, 1):
    lines.append(f'  {i}. {p["discount_pct"]}% OFF | ${int(p["last_price"])} (lista ${int(p["list_price"])}) | {p["name"][:55]}')

lines.append('\nTOP 10 MAYOR MARGEN:')
margin = conn.execute("""
    SELECT name, last_price, list_price, (list_price - last_price) as margin
    FROM products WHERE list_price > last_price AND last_price > 0
    ORDER BY margin DESC LIMIT 10
""").fetchall()
for i, p in enumerate(margin, 1):
    lines.append(f'  {i}. Margen ${int(p["margin"])} | ${int(p["last_price"])} vs ${int(p["list_price"])} | {p["name"][:50]}')

conn.close()

output = '\n'.join(lines)
with open('output/cetrogar_scan.txt', 'w', encoding='utf-8') as f:
    f.write(output)
print(output)

sniffer.close()
