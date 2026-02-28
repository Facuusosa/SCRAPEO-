import sqlite3
import os

p = "targets/fravega/fravega_monitor.db"
conn = sqlite3.connect(p)
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(products)")
cols = [r[1] for r in cursor.fetchall()]
print(f"Columns: {cols}")

cursor.execute("SELECT name, title, last_price, list_price, discount_pct FROM products LIMIT 5")
rows = cursor.fetchall()
for r in rows:
    print(r)
conn.close()
