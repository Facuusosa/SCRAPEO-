import logging
from targets.casadelaudio.sniffer_casadelaudio import CasaDelAudioSniffer

logging.basicConfig(level=logging.INFO, format='%(message)s')

sniffer = CasaDelAudioSniffer()
results = sniffer.run_cycle(['celulares', 'smart-tv'])

for r in results:
    print(f'\n=== {r.category.upper()} ({r.products_found} prods) ===')
    for p in r.products[:10]:
        print(f'  - {p.discount_pct}% OFF | ${p.current_price:,.0f} | {p.name[:60]}')

sniffer.close()
