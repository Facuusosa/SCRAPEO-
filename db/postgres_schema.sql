-- 🏛️ ODISEO MASTER SCHEMA (Postgres Production)

-- 1. Usuarios
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2. Suscripciones
CREATE TABLE IF NOT EXISTS subscriptions (
    user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    tier TEXT DEFAULT 'free',
    status TEXT DEFAULT 'inactive',
    expires_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. Telegram Link
CREATE TABLE IF NOT EXISTS telegram_users (
    id SERIAL PRIMARY KEY,
    user_id TEXT UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    telegram_id TEXT UNIQUE,
    tier TEXT DEFAULT 'free',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. Feed de Oportunidades
CREATE TABLE IF NOT EXISTS opportunities (
    id SERIAL PRIMARY KEY,
    product_id TEXT NOT NULL,
    name TEXT NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    gap_teorico REAL,
    margen_odiseo REAL,
    stock_validado INTEGER DEFAULT 0,
    store TEXT,
    url TEXT,
    confirmed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 5. Índices de Performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe ON subscriptions(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_telegram_tid ON telegram_users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_opportunities_pid ON opportunities(product_id);
CREATE INDEX IF NOT EXISTS idx_opportunities_date ON opportunities(confirmed_at);
