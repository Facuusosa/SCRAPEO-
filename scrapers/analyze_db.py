"""Analizar deals en categorias de alta rotacion (electrónica)."""
import sqlite3, json

db = "targets/fravega/fravega_monitor.db"
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row

# Categorias electronica
elec_cats = [
    "celulares-y-smartphones%",
    "tv-y-video%",
    "computacion%",
    "gaming%",
    "audio%",
    "informatica%",
    "electronica%",
]

result = {}

# Stats por categoria electronica
for pattern in elec_cats:
    rows = conn.execute(f"""
        SELECT category, COUNT(*) as n,
               ROUND(AVG(last_price), 0) as avg_price,
               ROUND(MIN(last_price), 0) as min_price,
               COUNT(CASE WHEN list_price > 0 AND last_price < list_price THEN 1 END) as with_disc,
               ROUND(AVG(CASE WHEN list_price > 0 AND last_price < list_price 
                   THEN (1.0-last_price*1.0/list_price)*100 END), 1) as avg_disc,
               ROUND(MAX(CASE WHEN list_price > 0 AND last_price < list_price 
                   THEN (1.0-last_price*1.0/list_price)*100 END), 1) as max_disc
        FROM products
        WHERE category LIKE '{pattern}' AND last_price > 0
        GROUP BY category
        ORDER BY avg_disc DESC
    """).fetchall()
    for r in rows:
        result[r['category']] = dict(r)

# Top deals en electrónica (>=10% descuento, ordenados por descuento)
deals = conn.execute("""
    SELECT title, last_price, list_price, brand_name, category, image_url,
           ROUND((1.0-last_price*1.0/list_price)*100, 1) as discount,
           ROUND(list_price - last_price, 0) as savings
    FROM products
    WHERE last_price > 0 AND list_price > 0 AND last_price < list_price
          AND (category LIKE 'celulares%' OR category LIKE 'tv-%' OR category LIKE 'computacion%' 
               OR category LIKE 'gaming%' OR category LIKE 'audio%' OR category LIKE 'informatica%')
          AND ((1.0-last_price*1.0/list_price)*100) >= 10
    ORDER BY discount DESC
    LIMIT 40
""").fetchall()

# Top deals electrónica por ganancia absoluta
big_deals = conn.execute("""
    SELECT title, last_price, list_price, brand_name, category,
           ROUND((1.0-last_price*1.0/list_price)*100, 1) as discount,
           ROUND(list_price - last_price, 0) as profit
    FROM products
    WHERE last_price > 0 AND list_price > 0 AND last_price < list_price
          AND (category LIKE 'celulares%' OR category LIKE 'tv-%' OR category LIKE 'computacion%' 
               OR category LIKE 'gaming%' OR category LIKE 'audio%' OR category LIKE 'informatica%')
    ORDER BY profit DESC
    LIMIT 20
""").fetchall()

conn.close()

output = {
    "categorias_electronica": result,
    "top_deals_por_descuento": [dict(r) for r in deals],
    "top_deals_por_ganancia": [dict(r) for r in big_deals],
}

with open("output/electronica_analysis.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Categorias electronica encontradas: {len(result)}")
print(f"Deals con >=10% descuento: {len(deals)}")
print(f"Deals por ganancia absoluta: {len(big_deals)}")
