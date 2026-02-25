import sqlite3
import os
import sys

# Agregar root al path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

DB_PATH = os.path.join(PROJECT_ROOT, "web", "odiseo_users.db")
MIGRATIONS_DIR = os.path.join(PROJECT_ROOT, "db", "migrations")

def run_migrations():
    print(f"🚀 INICIANDO MIGRACIONES DE DB...")
    print(f"📂 DB Target: {DB_PATH}")
    
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Conectar a la DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabla para trackear que migraciones se corrieron
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS _migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Obtener archivos de migración ordenados
    migration_files = sorted([f for f in os.listdir(MIGRATIONS_DIR) if f.endswith(".sql")])
    
    applied_count = 0
    
    for filename in migration_files:
        # Verificar si ya se aplicó
        cursor.execute("SELECT id FROM _migrations WHERE name = ?", (filename,))
        if cursor.fetchone():
            print(f"  ⏭️  Saltando {filename} (ya aplicada)")
            continue
            
        print(f"  ⚙️  Aplicando {filename}...")
        
        with open(os.path.join(MIGRATIONS_DIR, filename), "r", encoding="utf-8") as f:
            sql = f.read()
            
        try:
            cursor.executescript(sql)
            cursor.execute("INSERT INTO _migrations (name) VALUES (?)", (filename,))
            conn.commit()
            print(f"    ✅ Ok")
            applied_count += 1
        except Exception as e:
            conn.rollback()
            print(f"    ❌ ERROR en {filename}: {e}")
            conn.close()
            sys.exit(1)
            
    conn.close()
    
    if applied_count > 0:
        print(f"\n✨ MIGRATIONS OK: {applied_count} nuevas migraciones aplicadas.")
    else:
        print("\n✅ DB ya está actualizada.")

if __name__ == "__main__":
    run_migrations()
