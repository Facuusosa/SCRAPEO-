"""Scan PROFUNDO de On City - TODAS las categorias, sin limite."""
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

from targets.oncity.sniffer_oncity import OnCitySniffer

sniffer = OnCitySniffer()

# TODAS las categorias que tienen productos relevantes
categories = [
    # Tecnologia
    'celulares',
    'notebooks', 
    'tablets',
    'smartwatches',
    'consolas',
    'gaming',
    'informatica',
    
    # Audio/TV
    'smart-tv',
    'audio',
    'soundbar',
    
    # Electrodomesticos
    'aires',
    'heladeras',
    'lavarropas',
    'cocinas',
    'microondas',
    'cafeteras',
]

# Sin limite (hasta 2000 por categoria)
results = sniffer.run_cycle(categories, size=2000)

lines = []
lines.append('='*60)
lines.append('SCAN PROFUNDO ON CITY - TODAS LAS CATEGORIAS')
lines.append('='*60)
lines.append('')

total_products = 0
for r in results:
    total_products += r.products_found
    status = 'OK' if r.success else 'VACIO' if r.products_found == 0 else 'ERROR'
    lines.append(f'  {r.category:20s} | {r.products_found:4d} prods | {r.glitches_found} glitches | {r.duration_seconds:.1f}s | {status}')

lines.append(f'\nTOTAL: {total_products} productos scrapeados')

with open('output/oncity_deep_scan.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print('\n'.join(lines))
sniffer.close()
print('\nScan profundo completado')
