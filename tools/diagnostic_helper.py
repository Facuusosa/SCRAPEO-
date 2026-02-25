import sqlite3
import os
import json
from datetime import datetime

PROJECT_ROOT = os.getcwd()
USER_DB = os.path.join(PROJECT_ROOT, "web", "odiseo_users.db")
TARGETS_DIR = os.path.join(PROJECT_ROOT, "data", "databases")

def get_db_stats():
    stats = {
        "user_db": {
            "exists": os.path.exists(USER_DB),
            "total_opps": 0,
            "confirmed_10plus": 0,
            "last_insert": None,
            "distribution": {}
        },
        "monitor_dbs": []
    }

    if stats["user_db"]["exists"]:
        try:
            conn = sqlite3.connect(USER_DB)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Total opps
            cursor.execute("SELECT COUNT(*) FROM opportunities")
            stats["user_db"]["total_opps"] = cursor.fetchone()[0]
            
            # Margen >= 10
            cursor.execute("SELECT COUNT(*) FROM opportunities WHERE margen_odiseo >= 10")
            stats["user_db"]["confirmed_10plus"] = cursor.fetchone()[0]
            
            # Distribution
            cursor.execute("SELECT store, COUNT(*) as count FROM opportunities GROUP BY store")
            for row in cursor.fetchall():
                stats["user_db"]["distribution"][row['store'] or 'Desconocido'] = row['count']
                
            # Last insert
            cursor.execute("SELECT MAX(confirmed_at) FROM opportunities")
            stats["user_db"]["last_insert"] = cursor.fetchone()[0]
            
            conn.close()
        except Exception as e:
            stats["user_db"]["error"] = str(e)

    # Scraper Databases (Global inventory)
    if os.path.exists(TARGETS_DIR):
        for db_file in os.listdir(TARGETS_DIR):
            if db_file.endswith(".db"):
                db_path = os.path.join(TARGETS_DIR, db_file)
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM products")
                    count = cursor.fetchone()[0]
                    stats["monitor_dbs"].append({"name": db_file, "count": count})
                    conn.close()
                except:
                    pass

    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    get_db_stats()
