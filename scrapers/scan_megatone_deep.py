"""Deep Scan Megatone - Extraccion total."""
import logging
import sqlite3
from targets.megatone.sniffer_megatone import MegatoneSniffer

logging.basicConfig(level=logging.INFO, format='%(message)s')

sniffer = MegatoneSniffer()

categories = [
    'celulares', 'notebooks', 'tablets', 'smart-tv', 'aires', 
    'heladeras', 'lavarropas', 'cocinas', 'audio', 'consolas',
    'microondas', 'termotanques', 'licuadoras', 'cafeteras'
]

# Pedimos 500 por categoria (Doofinder tiene muchos)
results = sniffer.run_cycle(categories, size=500)

lines = []
lines.append('='*60)
lines.append('DEEP SCAN MEGATONE - RESULTADOS')
lines.append('='*60)

total = 0
for r in results:
    total += r.products_found
    lines.append(f'  {r.category:15s} | {r.products_found:4d} prods | {r.duration_seconds:.1f}s')

lines.append(f'\nTOTAL SCRAPEADO: {total} productos')

# Analisis de Oportunidades
conn = sqlite3.connect('megatone_monitor.db')
conn.row_factory = sqlite3.Row

lines.append('\n🔥 TOP 15 MEJORES DESCUENTOS EN MEGATONE:')
top = conn.execute("""
    SELECT name, brand, last_price, list_price, discount_pct, url
    FROM products 
    WHERE discount_pct > 0 AND last_price > 50000
    ORDER BY discount_pct DESC LIMIT 15
""").fetchall()

for i, p in enumerate(top, 1):
    lines.append(f'  {i}. {p["discount_pct"]}% OFF | ${p["last_price"]:,.0f} (Lista ${p["list_price"]:,.0f}) | {p["name"][:50]}')

lines.append('\n💰 PRODUCTOS CON MAYOR MARGEN ($):')
margins = conn.execute("""
    SELECT name, (list_price - last_price) as margin, last_price, list_price
    FROM products 
    WHERE last_price > 0 AND list_price > last_price
    ORDER BY margin DESC LIMIT 10
""").fetchall()

for i, p in enumerate(margins, 1):
    lines.append(f'  {i}. Margen ${p["margin"]:,.0f} | ${p["last_price"]:,.0f} vs ${p["list_price"]:,.0f} | {p["name"][:50]}')

conn.close()

output = '\n'.join(lines)
with open('output/megatone_analysis.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print(output)
sniffer.close()
