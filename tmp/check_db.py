import sqlite3
import os

paths = [
    "data/databases/casadelaudio_monitor.db",
    "data/databases/cetrogar_monitor.db",
    "data/databases/fravega_monitor.db",
    "data/databases/megatone_monitor.db",
    "data/databases/newsan_monitor.db",
    "data/databases/oncity_monitor.db",
    "targets/fravega/fravega_monitor.db",
    "cetrogar_monitor.db",
    "megatone_monitor.db",
    "oncity_monitor.db"
]

for p in paths:
    if os.path.exists(p):
        try:
            conn = sqlite3.connect(p)
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM products")
            count = cursor.fetchone()[0]
            print(f"{p}: {count} products")
            conn.close()
        except Exception as e:
            print(f"{p}: Error - {e}")
    else:
        print(f"{p}: Not found")
