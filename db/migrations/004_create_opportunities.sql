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
CREATE INDEX IF NOT EXISTS idx_opp_pid ON opportunities(product_id);
CREATE INDEX IF NOT EXISTS idx_opp_date ON opportunities(confirmed_at);
