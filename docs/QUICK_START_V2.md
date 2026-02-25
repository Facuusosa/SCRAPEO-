# ⚡ QUICK START — Sniffer V2 en 5 minutos

> "De candidatos a oportunidades confirmadas. Sin falsas alarmas."

---

## 📦 Instalación

### 1. Dependencias

```bash
pip install playwright curl-cffi
python -m playwright install chromium
```

### 2. Clonar / actualizar repo

```bash
cd C:\Users\Facun\OneDrive\Escritorio\FRAVEGA
git pull  # (si tenés git)
```

---

## 🎯 Modo 1: Testing Local (Rápido)

```bash
# Ejecutar 1 ciclo (scan todas las categorías, encuentra oportunidades)
python targets/fravega/sniffer_fravega_v2.py

# Output esperado:
# 🔍 Escaneando: computacion/notebooks
#   📦 computacion/notebooks: 20 productos
# ✅ 15 productos válidos
# 🎯 CANDIDATO: Lenovo IdeaPad... | Gap: 20.5% | Margen: 15.5%
#   ✅ Margen Odiseo OK (15.5%) → Validando stock...
#   ✅ Stock VALIDADO (12500ms)
# 🚀 ╔════════════════════════════════════════
# 🚀 ║ OPORTUNIDAD ODISEO CONFIRMADA
# 🚀 ║ Producto: Lenovo IdeaPad 15...
# 🚀 ║ Precio Fravega: $700,000
# 🚀 ║ Gap: 20.5% | Margen: 15.5%
# 🚀 ║ Stock: ✅ VALIDADO | Tiempo: 12500ms
# 🚀 ╚════════════════════════════════════════
```

**Tiempo esperado:** 2-5 minutos (depende del # de categorías)

---

## 🎯 Modo 2: Con Proxy (Anti-WAF)

```bash
# Webshare example ($30/mes)
python targets/fravega/sniffer_fravega_v2.py \
  --proxy http://username:password@proxy.webshare.io:80
```

---

## 🎯 Modo 3: Bridge (Multi-sniffer)

Ejecutar Fravega + otros targets en paralelo:

```bash
# V2 solo para Fravega
python web/bridge_v2.py --sniffers fravega --versions v2

# Multi-target (cuando Megatone/Cetrogar tengan V2)
python web/bridge_v2.py \
  --sniffers fravega,megatone,cetrogar \
  --versions v2,v2,v2
```

---

## 📊 Resultados

### DB Generada

Archivo: `targets/fravega/fravega_monitor_v2.db`

```sql
-- Tabla: opportunities
-- Cada fila = 1 oportunidad CONFIRMADA
SELECT * FROM opportunities;

-- Resultado ejemplo:
| id | product_id | product_name      | current_price | gap_teorico | margen_odiseo | stock_validado | tiempo_validacion_ms | confirmed_at           |
|----|------------|-------------------|---------------|-------------|---------------|----------------|----------------------|------------------------|
| 1  | prod-123  | Lenovo IdeaPad... | 700000        | 20.5        | 15.5          | 1              | 12500                | 2026-02-25T02:45:30Z   |
| 2  | prod-456  | Dell XPS 13...    | 950000        | 18.2        | 13.2          | 1              | 11200                | 2026-02-25T02:46:15Z   |
```

### Alertas

Tabla: `alerts`

```sql
SELECT * FROM alerts WHERE alert_type = 'oportunidad';

| id | product_id | alert_type   | message                       | timestamp              |
|----|-----------|--------------|-------------------------------|------------------------|
| 1  | prod-123  | oportunidad  | Margen 15.5% | Stock validado | 2026-02-25T02:45:30Z   |
| 2  | prod-456  | oportunidad  | Margen 13.2% | Stock validado | 2026-02-25T02:46:15Z   |
```

---

## 🔧 Calibración

### ¿Pocos candidatos? (< 2)

**Problema:** Gap >= 18% es muy restrictivo  
**Solución:**

```python
# En sniffer_fravega_v2.py, línea ~400:

if gap >= 18:  # ← Cambiar a 15 o 12
    self.stats["candidatos"] += 1
```

### ¿Muchos falsos negativos? (Candidatos rechazados por margen)

**Problema:** Margen >= 10% es muy alto  
**Solución:**

```python
# En sniffer_fravega_v2.py, línea ~420:

if margen < 10:  # ← Cambiar a 8 o 5
    return None
```

### ¿Muchos falsos positivos? (Stock validation fallando)

**Problema:** Playwright no puede agregar al carrito  
**Debugging:**

```python
# Agregar --debug flag (futuro)
python targets/fravega/sniffer_fravega_v2.py --debug

# Esto guarda screenshots de fallos en /output/screenshots/
```

---

## 📈 Métricas

**Ejemplo real (20 productos, Lenovo notebooks):**

```
Input:        20 productos
├─ Gap >= 18% (candidatos):    3 productos (15%)
│  ├─ Margen >= 10%:           2 productos (67% de candidatos)
│  └─ Stock validation:        2/2 OK (100% de margen)
├─ Final:                      2 oportunidades confirmadas (10%)
└─ Tiempo total:               ~35 segundos (20s GraphQL + 15s Playwright)
```

---

## 🚀 Integración con SaaS

### Paso 1: Conectar a la DB real

```python
# En bridge_v2.py o web/api/
from core.database import Database

db = Database("targets/fravega/fravega_monitor_v2.db")
opps = db.get_opportunities(limit=10, recent_only=True)

# JSON para Frontend
return {
    "opportunities": [
        {
            "id": opp.product_id,
            "name": opp.product_name,
            "margin": opp.margen_odiseo,
            "url": opp.url,
            "validated_at": opp.confirmed_at,
        }
        for opp in opps
    ]
}
```

### Paso 2: WebSocket en tiempo real

```typescript
// web/components/RealTimeBridge.tsx
useEffect(() => {
    const ws = new WebSocket('ws://localhost:3001/events');
    
    ws.onmessage = (event) => {
        const { type, data } = JSON.parse(event.data);
        
        if (type === 'opportunity') {
            // Nueva oportunidad confirmada
            addToFeed(data);
            playNotificationSound();
        }
    };
}, []);
```

### Paso 3: Alertas a usuarios

```python
# telegram_bot.py
for opp in opportunities:
    message = f"""
    🚀 OPORTUNIDAD CONFIRMADA
    
    📦 {opp.name}
    💰 ${opp.current_price:,.0f}
    📊 Margen: {opp.margen_odiseo:.1f}%
    ✅ Stock validado
    
    Link: {opp.url}
    """
    
    telegram_bot.send_message(chat_id, message)
```

---

## ❌ Troubleshooting

### Error: `WAFBlockedError: 403`

```
[FRAVEGA-V2] ERROR [fravega-v2] GraphQL Error: 403 Forbidden
```

**Causa:** Cloudflare bloqueó la IP  
**Solución:**
1. Esperar 10-20 minutos
2. Usar proxy (Webshare, BrightData)
3. Agregar delays más largos

```python
# En sniffer_fravega_v2.py:
time.sleep(random.uniform(5, 10))  # Esperar más
```

### Error: `Playwright timeout`

```
ERROR sniffer_v2: Esperando producto: timeout después de 30s
```

**Causa:** Frávega está lento o está bloqueando Playwright  
**Solución:**
1. Aumentar timeout
2. Usar headless=False para debugging
3. Cambiar user-agent

```python
# En StockValidator:
await page.goto(product_url, wait_until="domcontentloaded", timeout=60000)
```

### Error: `Module not found: playwright`

```
ModuleNotFoundError: No module named 'playwright'
```

**Causa:** No instalado  
**Solución:**
```bash
pip install playwright
python -m playwright install chromium
```

---

## 📊 Monitoreo

### Ver logs en tiempo real

```bash
# En otra terminal
tail -f output/sniffer_v2.log
```

### Ver estado de la DB

```bash
# SQLite CLI
sqlite3 targets/fravega/fravega_monitor_v2.db

# Listar oportunidades
SELECT COUNT(*) as total, AVG(margen_odiseo) as margen_promedio 
FROM opportunities 
WHERE confirmed_at > datetime('now', '-1 hour');

# Output:
# total | margen_promedio
# 5     | 12.3
```

---

## 🎯 Resumen

| Paso | Acción | Tiempo |
|------|--------|--------|
| 1 | Instalar deps | 2 min |
| 2 | Correr sniffer | 3-5 min |
| 3 | Ver oportunidades | Instantáneo |
| 4 | Integrar a SaaS | 1-2 horas |

**Total:** De 0 a MVP SaaS = **~2 horas**

---

## 📚 Docs relacionados

- `REFACTOR_V2_INTEGRATION.md` — Detalles técnicos del pipeline
- `sniffer_fravega_v2.py` — Código fuente (100% comentado)
- `bridge_v2.py` — Orquestador multi-sniffer

¿Preguntas? Mirá la sección de troubleshooting o lee el código comentado. 🚀
