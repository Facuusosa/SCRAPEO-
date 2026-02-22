"""Scrape categorias faltantes de On City con paths correctos."""
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

from targets.oncity.sniffer_oncity import OnCitySniffer, ONCITY_CATEGORIES

# Paths correctos encontrados en el arbol de categorias
MISSING_CATS = {
    'heladeras': 'electrodomesticos/heladeras-y-freezers/heladeras',
    'freezers': 'electrodomesticos/heladeras-y-freezers/freezers',
    'lavarropas': 'electrodomesticos/lavado-y-secado/lavarropas',
    'lavasecarropas': 'electrodomesticos/lavado-y-secado/lavasecarropas',
    'cafeteras': 'electrodomesticos/pequenos-electro-de-cocina/cafeteras',
    'freidoras': 'electrodomesticos/pequenos-electro-de-cocina/freidoras',
    'aspiradoras': 'electrodomesticos/pequenos-electro-de-hogar/aspiradoras-y-barredoras',
    'tablets': 'tecnologia/informatica/tablets',
}

# Agregar al mapa
ONCITY_CATEGORIES.update(MISSING_CATS)

sniffer = OnCitySniffer()

results = sniffer.run_cycle(list(MISSING_CATS.keys()), size=500)

lines = []
lines.append('CATEGORIAS FALTANTES SCRAPEADAS:')
total = 0
for r in results:
    total += r.products_found
    lines.append(f'  {r.category:20s} | {r.products_found:4d} prods | {r.duration_seconds:.1f}s')

lines.append(f'\nNuevos productos: {total}')

# Total en DB
import sqlite3
conn = sqlite3.connect('oncity_monitor.db')
total_db = conn.execute('SELECT COUNT(*) FROM products').fetchone()[0]
lines.append(f'Total en DB ahora: {total_db}')
conn.close()

output = '\n'.join(lines)
print(output)
with open('output/oncity_missing_cats.txt', 'w', encoding='utf-8') as f:
    f.write(output)

sniffer.close()
