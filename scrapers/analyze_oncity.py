"""Analisis completo de On City DB despues del deep scan."""
import sqlite3

conn = sqlite3.connect('oncity_monitor.db')
conn.row_factory = sqlite3.Row

lines = []

total = conn.execute('SELECT COUNT(*) as n FROM products').fetchone()['n']
lines.append(f'TOTAL PRODUCTOS EN DB: {total}')
lines.append('')

# Stats generales
stats = conn.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN discount_pct > 0 THEN 1 END) as con_descuento,
        ROUND(AVG(CASE WHEN discount_pct > 0 THEN discount_pct END), 1) as avg_disc,
        ROUND(MAX(discount_pct), 1) as max_disc,
        COUNT(CASE WHEN discount_pct >= 30 THEN 1 END) as desc_30plus,
        COUNT(CASE WHEN discount_pct >= 40 THEN 1 END) as desc_40plus,
        COUNT(CASE WHEN discount_pct >= 50 THEN 1 END) as desc_50plus,
        COUNT(CASE WHEN stock = 0 THEN 1 END) as sin_stock
    FROM products WHERE last_price > 0
""").fetchone()

lines.append('ESTADISTICAS GENERALES:')
lines.append(f'  Total productos: {stats["total"]}')
lines.append(f'  Con descuento: {stats["con_descuento"]} ({round(stats["con_descuento"]*100/stats["total"],1)}%)')
lines.append(f'  Descuento promedio: {stats["avg_disc"]}%')
lines.append(f'  Descuento maximo: {stats["max_disc"]}%')
lines.append(f'  30%+ descuento: {stats["desc_30plus"]}')
lines.append(f'  40%+ descuento: {stats["desc_40plus"]}')
lines.append(f'  50%+ descuento: {stats["desc_50plus"]}')
lines.append('')

# Categorias
cats = conn.execute("""
    SELECT category, COUNT(*) as n, 
           ROUND(AVG(discount_pct),1) as avg_disc,
           ROUND(MAX(discount_pct),1) as max_disc,
           COUNT(CASE WHEN discount_pct >= 30 THEN 1 END) as hot_deals
    FROM products WHERE last_price > 0 
    GROUP BY category ORDER BY n DESC
""").fetchall()
lines.append('CATEGORIAS:')
for c in cats:
    cat = str(c['category'] or 'sin-cat')[:40]
    lines.append(f'  {cat} | {c["n"]} prods | avg: {c["avg_disc"]}% | max: {c["max_disc"]}% | hot deals: {c["hot_deals"]}')

lines.append('')
lines.append('TOP 20 DESCUENTOS:')
top = conn.execute("""
    SELECT name, brand, last_price, list_price, discount_pct, url, category
    FROM products WHERE discount_pct > 0 
    ORDER BY discount_pct DESC LIMIT 20
""").fetchall()
for i, p in enumerate(top, 1):
    lines.append(f'  {i}. {p["discount_pct"]}% OFF')
    lines.append(f'     ${int(p["last_price"])} (lista ${int(p["list_price"])})')
    lines.append(f'     {p["brand"]} - {p["name"][:60]}')
    lines.append(f'     {p["url"]}')
    lines.append('')

lines.append('TOP 20 MAYOR MARGEN ($):')
margin = conn.execute("""
    SELECT name, brand, last_price, list_price, (list_price - last_price) as margin, url
    FROM products WHERE list_price > last_price AND last_price > 0 
    ORDER BY margin DESC LIMIT 20
""").fetchall()
for i, p in enumerate(margin, 1):
    lines.append(f'  {i}. Margen: ${int(p["margin"])}')
    lines.append(f'     ${int(p["last_price"])} vs ${int(p["list_price"])}')
    lines.append(f'     {p["brand"]} - {p["name"][:60]}')
    lines.append(f'     {p["url"]}')
    lines.append('')

# Marcas con mas descuento
lines.append('TOP 15 MARCAS CON MAS DESCUENTO:')
brands = conn.execute("""
    SELECT brand, COUNT(*) as n, 
           ROUND(AVG(discount_pct),1) as avg_disc,
           ROUND(MAX(discount_pct),1) as max_disc,
           COUNT(CASE WHEN discount_pct >= 30 THEN 1 END) as hot
    FROM products WHERE last_price > 0 AND discount_pct > 0
    GROUP BY brand 
    HAVING COUNT(*) >= 5
    ORDER BY avg_disc DESC LIMIT 15
""").fetchall()
for b in brands:
    lines.append(f'  {b["brand"][:25]:25s} | {b["n"]} prods | avg: {b["avg_disc"]}% | max: {b["max_disc"]}% | hot: {b["hot"]}')

# Alertas
alerts = conn.execute('SELECT COUNT(*) as n FROM alerts').fetchone()['n']
lines.append(f'\nALERTAS REGISTRADAS: {alerts}')

conn.close()

output = '\n'.join(lines)
with open('output/oncity_deep_analysis.txt', 'w', encoding='utf-8') as f:
    f.write(output)
print(output)
