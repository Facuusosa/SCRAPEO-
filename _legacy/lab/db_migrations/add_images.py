
import sqlite3

db_path = "fravega_monitor.db"

def add_image_column():
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute("ALTER TABLE products ADD COLUMN image_url TEXT")
            print("✅ Columna 'image_url' agregada.")
    except Exception as e:
        print(f"ℹ️ {e}")

if __name__ == "__main__":
    add_image_column()
