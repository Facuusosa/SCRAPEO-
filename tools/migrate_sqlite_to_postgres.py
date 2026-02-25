import sqlite3
import os
import sys
import psycopg2
from psycopg2.extras import execute_values

# Configuración
SQLITE_DB = "web/odiseo_users.db"
POSTGRES_URL = os.environ.get("DATABASE_URL")

def migrate():
    if not POSTGRES_URL:
        print("❌ Error: DATABASE_URL no definida.")
        return

    print("🚀 Iniciando migración SQLite -> Postgres...")
    
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_conn.row_factory = sqlite3.Row
        pg_conn = psycopg2.connect(POSTGRES_URL)
        pg_cur = pg_conn.cursor()

        # 1. Migrar Usuarios
        print("  👤 Migrando usuarios...")
        users = sqlite_conn.execute("SELECT * FROM users").fetchall()
        if users:
            execute_values(pg_cur, 
                "INSERT INTO users (id, email, password_hash, created_at) VALUES %s ON CONFLICT DO NOTHING",
                [(u['id'], u['email'], u['password_hash'], u['created_at']) for u in users])

        # 2. Migrar Suscripciones
        print("  💳 Migrando suscripciones...")
        subs = sqlite_conn.execute("SELECT * FROM subscriptions").fetchall()
        if subs:
            execute_values(pg_cur,
                "INSERT INTO subscriptions (user_id, stripe_customer_id, stripe_subscription_id, tier, status) VALUES %s ON CONFLICT DO NOTHING",
                [(s['user_id'], s['stripe_customer_id'], s['stripe_subscription_id'], s['tier'], s['status']) for s in subs])

        # 3. Migrar Telegram
        print("  📱 Migrando telegram_users...")
        t_users = sqlite_conn.execute("SELECT * FROM telegram_users").fetchall()
        if t_users:
            execute_values(pg_cur,
                "INSERT INTO telegram_users (user_id, telegram_id, tier, created_at) VALUES %s ON CONFLICT DO NOTHING",
                [(tu['user_id'], tu['telegram_id'], tu['tier'], tu['created_at']) for tu in t_users])

        pg_conn.commit()
        print("\n✅ MIGRACIÓN EXITOSA")

    except Exception as e:
        print(f"\n❌ ERROR de migración: {e}")
    finally:
        if 'sqlite_conn' in locals(): sqlite_conn.close()
        if 'pg_conn' in locals(): pg_conn.close()

if __name__ == "__main__":
    migrate()
