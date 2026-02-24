import logging
from targets.newsan.sniffer_newsan import NewsanSniffer

logging.basicConfig(level=logging.INFO, format='%(message)s')

sniffer = NewsanSniffer()
results = sniffer.run_cycle(['celulares'])

for r in results:
    print(f'\n=== {r.category} ===')
    print(f'  Productos found: {r.products_found}')
    for p in r.products[:10]:
        print(f'  - {p.discount_pct}% OFF | ${p.current_price:,.0f} | {p.name[:60]}')

sniffer.close()
