---
description: Analizar precios y encontrar oportunidades de reventa
---

# Analyze Prices

// turbo-all

## Steps

1. **Ver estado de la DB**:
```bash
python -c "from core import Database; db = Database('targets/fravega/fravega_monitor.db'); print(db.get_stats())"
```

2. **Top descuentos**:
```bash
python -c "
from core import Database
db = Database('targets/fravega/fravega_monitor.db')
for d in db.get_biggest_discounts(min_discount=20, limit=15):
    print(f\"{d['name'][:50]:50s} | \${d['current_price']:>10,.0f} | -{d['real_discount']}% | Ahorro: \${d['savings']:,.0f}\")
"
```

3. **Glitches recientes**:
```bash
python -c "
from core import Database
db = Database('targets/fravega/fravega_monitor.db')
for g in db.get_recent_glitches(hours=48):
    print(f\"🚨 [{g['severity']}] {g['product_name'][:50]} - \${g['current_price']:,.0f} - {g['reason']}\")
"
```

4. **Comparar entre fuentes** (cuando tengamos múltiples targets):
```bash
python -c "
from core import Database
db = Database('targets/fravega/fravega_monitor.db')
results = db.compare_prices_across_sources('%iPhone%')
for r in results:
    print(f\"{r['source']:15s} | \${r['best_price']:>10,.0f} - \${r['worst_price']:>10,.0f} | visto {r['times_seen']}x\")
"
```
