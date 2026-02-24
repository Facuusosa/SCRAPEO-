"""Test rapido del sniffer de On City."""
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

from targets.oncity.sniffer_oncity import OnCitySniffer

sniffer = OnCitySniffer()

# Test: solo celulares
results = sniffer.run_cycle(['celulares'], size=50)

for r in results:
    print(f'\n=== {r.category} ===')
    print(f'  Productos: {r.products_found}')
    print(f'  Glitches: {r.glitches_found}')
    print(f'  Errores: {len(r.errors)}')
    print(f'  Duracion: {r.duration_seconds}s')
    
    # Top 5 descuentos
    sorted_products = sorted(r.products, key=lambda p: p.discount_pct, reverse=True)
    print(f'\n  Top 5 descuentos:')
    for p in sorted_products[:5]:
        if p.discount_pct > 0:
            print(f'    {p.discount_pct:.0f}% OFF | ${p.current_price:,.0f} (era ${p.list_price:,.0f}) | {p.name[:50]}')

sniffer.close()
print('\nTest completado OK')
