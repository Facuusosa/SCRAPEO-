import logging
from targets.megatone.sniffer_megatone import MegatoneSniffer

logging.basicConfig(level=logging.INFO, format='%(message)s')

sniffer = MegatoneSniffer()
# Probamos con un par de categorias masivas
results = sniffer.run_cycle(['celulares', 'notebooks'])

total_found = 0
for r in results:
    total_found += r.products_found
    print(f'\n=== {r.category.upper()} ({r.products_found} prods) ===')
    for p in r.products[:5]:
        print(f'  - {p.discount_pct}% OFF | ${p.current_price:,.0f} | {p.name[:60]}')

print(f'\nTotal Megatone encontrado: {total_found} productos')
sniffer.close()
