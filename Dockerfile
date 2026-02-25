# --- STAGE 1: Build Node.js App ---
FROM node:18-slim AS builder
WORKDIR /app
COPY web/package*.json ./web/
WORKDIR /app/web
RUN npm install
COPY web/ .
RUN npm run build

# --- STAGE 2: Final Runtime ---
FROM node:18-slim
WORKDIR /app

# Instalar Python y dependencias de sistema necesaras para Playwright/Scrapers
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libphi-core \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Copiar App Node construida
COPY --from=builder /app/web/.next /app/web/.next
COPY --from=builder /app/web/public /app/web/public
COPY --from=builder /app/web/node_modules /app/web/node_modules
COPY --from=builder /app/web/package.json /app/web/package.json
COPY --from=builder /app/web/next.config.ts /app/web/next.config.ts

# Copiar Código Python y resto del repo
COPY core/ /app/core/
COPY targets/ /app/targets/
COPY scrapers/ /app/scrapers/
COPY tools/ /app/tools/
COPY db/ /app/db/

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt || echo "requirements.txt not found, skipping"
# Instalar Playwright browsers
RUN playwright install chromium --with-deps || echo "Playwright not installed or failed"

# Variables de entorno por defecto
ENV NODE_ENV production
ENV PORT 3000

# Exponer puertos
EXPOSE 3000

# Script de arranque (Web + Opcional Sniffer en background o via Cron de Railway)
CMD ["npm", "start", "--prefix", "web"]
