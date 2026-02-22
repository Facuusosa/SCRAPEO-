---
name: compare-excel
description: Cruzar datos del Excel de competidores con datos scrapeados para encontrar oportunidades
---

# Compare Excel: $ARGUMENTS

## Objetivo
Cruzar el archivo `Precios competidores.xlsx` con los datos de la DB para identificar:
1. Productos con diferencia de precio entre fuentes
2. Oportunidades de arbitraje (comprar barato en una, vender al precio de otra)
3. Tendencias de precios

## Pasos

### 1. Cargar el Excel
```python
import pandas as pd
from openpyxl import load_workbook

# Leer estructura del archivo
wb = load_workbook("Precios competidores.xlsx", read_only=True)
print(f"Hojas: {wb.sheetnames}")

for sheet in wb.sheetnames:
    ws = wb[sheet]
    print(f"\n--- {sheet} ---")
    for row in ws.iter_rows(min_row=1, max_row=5, values_only=True):
        print(row)

# Cargar con pandas para análisis
df = pd.read_excel("Precios competidores.xlsx", engine="openpyxl")
print(f"\nColumnas: {df.columns.tolist()}")
print(f"Filas: {len(df)}")
print(df.describe())
```

### 2. Cargar Datos de la DB
```python
from core import Database
db = Database("targets/fravega/fravega_monitor.db")

# Obtener todos los productos con descuento
deals = db.get_biggest_discounts(min_discount=10.0, limit=500)
df_db = pd.DataFrame(deals)
```

### 3. Normalizar y Cruzar
```python
# Normalizar nombres para matching
def normalize_name(name):
    return name.lower().strip()
    # Podés agregar: quitar acentos, stopwords, etc.

df["name_norm"] = df["producto"].apply(normalize_name)
df_db["name_norm"] = df_db["name"].apply(normalize_name)

# Merge por nombre normalizado
merged = pd.merge(
    df, df_db,
    left_on="name_norm", right_on="name_norm",
    how="inner",
    suffixes=("_excel", "_scrape")
)
print(f"Matches encontrados: {len(merged)}")
```

### 4. Calcular Oportunidades
```python
# Diferencia de precio entre Excel (competidores) y datos scrapeados
merged["diff"] = merged["precio_excel"] - merged["current_price"]
merged["diff_pct"] = (merged["diff"] / merged["current_price"] * 100).round(1)

# Oportunidades: donde nuestro precio es menor que el competidor
opportunities = merged[merged["diff"] > 0].sort_values("diff", ascending=False)
print(f"\nOportunidades de reventa: {len(opportunities)}")
for _, row in opportunities.head(20).iterrows():
    print(f"  {row['name'][:50]}")
    print(f"    Nuestro: ${row['current_price']:,.0f} | Competidor: ${row['precio_excel']:,.0f}")
    print(f"    Margen: ${row['diff']:,.0f} ({row['diff_pct']}%)")
```

### 5. Generar Excel de Reporte
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

wb = Workbook()
ws = wb.active
ws.title = "Oportunidades"

# Headers
headers = ["Producto", "Precio Nuestro", "Precio Competidor", "Diferencia", "Margen %"]
for col, h in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=h)
    cell.font = Font(bold=True)

# Data con FÓRMULAS (nunca hardcodear)
for i, (_, row) in enumerate(opportunities.iterrows(), 2):
    ws.cell(row=i, column=1, value=row["name"])
    ws.cell(row=i, column=2, value=row["current_price"])      # Input (azul)
    ws.cell(row=i, column=3, value=row["precio_excel"])        # Input (azul)
    ws.cell(row=i, column=4).value = f"=C{i}-B{i}"            # FÓRMULA
    ws.cell(row=i, column=5).value = f"=D{i}/B{i}*100"        # FÓRMULA

wb.save("output/oportunidades.xlsx")
```

### 6. Output Esperado
- `output/oportunidades.xlsx` con:
  - Hoja 1: Oportunidades de reventa ordenadas por margen
  - Hoja 2: Productos sin match (para investigar)
  - Hoja 3: Resumen por categoría
- Todas las celdas calculadas usan FÓRMULAS, no valores hardcodeados
