
import sqlite3

db_path = "fravega_monitor.db"

def fix_all_missing_cols():
    cols_to_add = [
        ("brand_name", "TEXT"),
        ("seller_name", "TEXT"),
        ("list_price", "REAL"),
        ("image_url", "TEXT")
    ]
    
    with sqlite3.connect(db_path) as conn:
        for col_name, col_type in cols_to_add:
            try:
                # Intenta añadir la columna
                conn.execute(f"ALTER TABLE products ADD COLUMN {col_name} {col_type}")
                print(f"✅ Columna '{col_name}' añadida con éxito.")
            except sqlite3.OperationalError as e:
                # Si falla porque ya existe, lo ignoramos
                if "duplicate column name" in str(e):
                    print(f"ℹ️ La columna '{col_name}' ya existía.")
                else:
                    print(f"⚠️ Error al añadir '{col_name}': {e}")
            except Exception as e:
                print(f"⚠️ Error desconocido en '{col_name}': {e}")

if __name__ == "__main__":
    print("Iniciando reparación de Base de Datos...")
    fix_all_missing_cols()
    print("Reparación finalizada.")
