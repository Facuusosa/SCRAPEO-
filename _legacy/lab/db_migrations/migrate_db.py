
import sqlite3

db_path = "fravega_monitor.db"

def migrate():
    try:
        with sqlite3.connect(db_path) as conn:
            # Try adding category if not exists
            try:
                conn.execute("ALTER TABLE products ADD COLUMN category TEXT")
                print("✅ Columna 'category' agregada.")
            except: pass
            
            # Add sku_code if not exists
            try:
                conn.execute("ALTER TABLE products ADD COLUMN sku_code TEXT")
                print("✅ Columna 'sku_code' agregada.")
            except: pass
            
            print("🚀 Migración completa.")
    except Exception as e:
        print(f"❌ Error fatal: {e}")

if __name__ == "__main__":
    migrate()
