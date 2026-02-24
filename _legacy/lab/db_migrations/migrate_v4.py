
import sqlite3

db_path = "fravega_monitor.db"

def migrate_v4():
    cols_to_add = [
        ("brand_name", "TEXT"),
        ("seller_name", "TEXT"),
        ("list_price", "REAL")
    ]
    
    with sqlite3.connect(db_path) as conn:
        for col_name, col_type in cols_to_add:
            try:
                conn.execute(f"ALTER TABLE products ADD COLUMN {col_name} {col_type}")
                print(f"✅ Columna '{col_name}' añadida.")
            except sqlite3.OperationalError:
                print(f"ℹ️ La columna '{col_name}' ya existe.")

if __name__ == "__main__":
    migrate_v4()
