---
name: analyze-prices
description: Analizar precios y encontrar oportunidades de reventa con margen
---

# Analyze Prices: $ARGUMENTS

## Objetivo
Analizar los datos de precios en la DB y/o Excel para encontrar las mejores oportunidades de compra y reventa.

## Pasos

### 1. Cargar Datos
```python
from core import Database
import pandas as pd

db = Database("targets/fravega/fravega_monitor.db")

# Opción A: Desde DB
stats = db.get_stats()
print(f"Total productos: {stats['total_products']}")
print(f"Fuentes: {stats['sources']}")
print(f"Categorías: {stats['categories']}")

# Opción B: Desde Excel
df = pd.read_excel("Precios competidores.xlsx", engine="openpyxl")
print(df.head())
print(df.columns.tolist())
```

### 2. Encontrar Mejores Descuentos
```python
# Top 20 productos con mayor descuento
deals = db.get_biggest_discounts(min_discount=25.0, limit=20)
for d in deals:
    print(f"  {d['name'][:50]} | ${d['current_price']:,.0f} | "
          f"-{d['real_discount']}% | Ahorro: ${d['savings']:,.0f} | {d['source']}")
```

### 3. Comparar Entre Tiendas
```python
# Buscar el mismo producto en diferentes fuentes
results = db.compare_prices_across_sources("%iPhone 15%")
for r in results:
    print(f"  {r['source']}: ${r['best_price']:,.0f} - ${r['worst_price']:,.0f}")
```

### 4. Calcular Margen de Reventa
```python
# Productos donde el precio de compra permite reventa con >15% margen
margin_threshold = 15.0  # %

for deal in deals:
    buy_price = deal['current_price']
    sell_price = deal['list_price']  # Precio de mercado
    margin = ((sell_price - buy_price) / buy_price) * 100
    
    if margin >= margin_threshold:
        profit = sell_price - buy_price
        print(f"  ✅ {deal['name'][:40]}")
        print(f"     Comprar: ${buy_price:,.0f} | Vender: ~${sell_price:,.0f}")
        print(f"     Ganancia: ${profit:,.0f} ({margin:.1f}%)")
```

### 5. Detectar Glitches Recientes
```python
glitches = db.get_recent_glitches(hours=24)
for g in glitches:
    print(f"  🚨 [{g['severity']}] {g['product_name']}")
    print(f"     Precio: ${g['current_price']:,.0f} | Razón: {g['reason']}")
```

### 6. Generar Reporte
- Exportar resultados a Excel con fórmulas (NO hardcodear valores)
- Incluir: Top deals, comparación entre tiendas, glitches, historial
- Guardar en `output/reporte_YYYY-MM-DD.xlsx`

### 7. Output Esperado
El análisis debe responder:
1. ¿Cuáles son los 10 productos más baratos por categoría?
2. ¿Dónde hay diferencia de precio entre tiendas? (arbitraje)
3. ¿Qué productos tienen margen de reventa >15%?
4. ¿Hubo glitches de precio en las últimas 24h?
5. ¿Cómo evolucionaron los precios esta semana?
