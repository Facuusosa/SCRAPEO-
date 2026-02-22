"""Scan completo de On City - categorias principales."""
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

from targets.oncity.sniffer_oncity import OnCitySniffer

sniffer = OnCitySniffer()

# Categorias de alto valor para arbitraje
categories = [
    'celulares',
    'notebooks', 
    'smart-tv',
    'audio',
    'aires',
    'heladeras',
    'lavarropas',
    'consolas',
]

results = sniffer.run_cycle(categories, size=200)

print('\n' + '='*60)
print('RESUMEN ON CITY')
print('='*60)

total_products = 0
total_glitches = 0
all_products = []

for r in results:
    total_products += r.products_found
    total_glitches += r.glitches_found
    all_products.extend(r.products)
    status = 'OK' if r.success else 'ERROR'
    print(f'  {r.category:20s} -> {r.products_found:4d} productos | {r.glitches_found} glitches | {r.duration_seconds:.1f}s | {status}')

print(f'\nTOTAL: {total_products} productos | {total_glitches} glitches')

# Top 10 mejores descuentos
sorted_all = sorted([p for p in all_products if p.discount_pct > 0], key=lambda p: p.discount_pct, reverse=True)
print(f'\nTOP 10 DESCUENTOS:')
for i, p in enumerate(sorted_all[:10], 1):
    print(f'  {i:2d}. {p.discount_pct:.0f}% OFF | ${p.current_price:,.0f} (lista ${p.list_price:,.0f}) | {p.name[:50]}')
    print(f'      Marca: {p.brand} | Cat: {p.category[:30]}')

# Top 10 mayor margen absoluto
sorted_margin = sorted([p for p in all_products if p.margin_potential > 0], key=lambda p: p.margin_potential, reverse=True)
print(f'\nTOP 10 MAYOR MARGEN ($):')
for i, p in enumerate(sorted_margin[:10], 1):
    print(f'  {i:2d}. ${p.margin_potential:,.0f} margen | ${p.current_price:,.0f} -> ${p.list_price:,.0f} | {p.name[:50]}')

sniffer.close()
print('\nScan completado OK')
