import sqlite3
import os

DB_PATHS = {
    "Fravega": "targets/fravega/fravega_monitor.db",
    "OnCity": "oncity_monitor.db",
    "Cetrogar": "cetrogar_monitor.db",
    "Megatone": "megatone_monitor.db",
    "Newsan": "newsan_monitor.db",
    "CasaDelAudio": "casadelaudio_monitor.db"
}

for store, rel_path in DB_PATHS.items():
    if os.path.exists(rel_path):
        conn = sqlite3.connect(rel_path)
        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        print(f"{store}: {count}")
        conn.close()
    else:
        print(f"{store}: NOT FOUND")
