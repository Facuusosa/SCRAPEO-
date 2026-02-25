import sqlite3
import os
import sys

# Agregar root al path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

DB_PATH = os.path.join(PROJECT_ROOT, "web", "odiseo_users.db")

def validate():
    print("🔍 VALIDANDO INTEGRIDAD DEL SCHEMA...")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: DB no encontrada en {DB_PATH}")
        sys.exit(1)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    required_tables = ["users", "subscriptions", "telegram_users", "opportunities"]
    errors = []
    
    for table in required_tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not cursor.fetchone():
            errors.append(f"Tabla faltante: {table}")
            continue
            
        print(f"  ✅ Tabla {table:15s}: OK")
        
        # Verificar FKs
        cursor.execute(f"PRAGMA foreign_key_check({table})")
        if cursor.fetchall():
            errors.append(f"Falla de FK en tabla: {table}")

    # Verificar indices clave
    expected_indices = ["idx_users_email", "idx_subscriptions_stripe_id", "idx_telegram_uid"]
    for idx in expected_indices:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND name='{idx}'")
        if not cursor.fetchone():
            # Algunos pueden tener nombres generados automaticamente si no se definieron explicitamente en migrations
            # Pero en este proyecto los definimos.
            errors.append(f"Índice faltante: {idx}")
        else:
            print(f"  ✅ Índice {idx:15s}: OK")

    conn.close()
    
    if errors:
        print("\n❌ SE ENCONTRARON ERRORES:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("\n✅ DB SCHEMA VALIDATED: Todo en orden.")
        sys.exit(0)

if __name__ == "__main__":
    validate()
