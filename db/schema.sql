-- 🏛️ ODISEO MASTER SCHEMA (MVP v2.0)
-- Optimized for SQLite & Postgres

-- 1. Tablas de Usuarios y Seguridad
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Sistema de Suscripciones (Stripe Integration)
CREATE TABLE IF NOT EXISTS subscriptions (
    user_id TEXT PRIMARY KEY,
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    tier TEXT DEFAULT 'free', -- 'free', 'vip', 'pro'
    status TEXT DEFAULT 'inactive', -- 'active', 'canceled', 'trailing', 'past_due'
    expires_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Identidad en Telegram (VIP Channel Access)
CREATE TABLE IF NOT EXISTS telegram_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE,
    telegram_id TEXT UNIQUE,
    tier TEXT DEFAULT 'free',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Oportunidades Confirmadas (Arbitrage Feed)
CREATE TABLE IF NOT EXISTS opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    gap_teorico REAL,
    margen_odiseo REAL,
    stock_validado INTEGER DEFAULT 0,
    store TEXT,
    url TEXT,
    confirmed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Índices para Performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_id ON subscriptions(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_telegram_uid ON telegram_users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_opp_pid ON opportunities(product_id);
CREATE INDEX IF NOT EXISTS idx_opp_date ON opportunities(confirmed_at);
