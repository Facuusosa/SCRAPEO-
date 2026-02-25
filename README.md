# 🏛️ PROYECTO ODISEO — Sistema de Inteligencia de Precios E-commerce

> *"No necesitamos saber cómo desarmar la bomba, solo qué piezas queremos de ella."*

## 🎯 Objetivo

Sistema escalable de monitoreo de precios en **múltiples e-commerce** argentinos (Frávega, MercadoLibre, Garbarino, etc.) para detectar **errores de precio (glitches)** y **oportunidades de compra** en tiempo real, con alertas automáticas.

## 🏗️ Arquitectura

```
FRAVEGA/
│
├── README.md                 # ← Estás acá
├── PROTOCOL.md               # Metodología Odiseo completa + Blueprint V4.0
├── PROMPTS_ARSENAL.md         # Arsenal de prompts para ingeniería inversa
│
├── core/                     # Código compartido entre TODOS los targets
│   └── (próximo: base_sniffer, notifier, database)
│
├── targets/                  # Un directorio por e-commerce
│   └── fravega/
│       ├── sniffer_fravega.py    # Motor principal (loop infinito, API GraphQL)
│       ├── cart_probe.py         # Verificador de precios ocultos en carrito
│       └── fravega_monitor.db    # Base de datos SQLite
│
├── tools/                    # Dashboards y reportes
│   ├── dashboard.py              # Panel de control en consola
│   ├── generate_report.py        # Generador de reporte HTML detallado
│   ├── generate_dashboard_html.py # Dashboard HTML visual
│   ├── generate_list.py          # Vista catálogo compacta
│   └── templates/
│       └── template_list.html
│
├── data/                     # Datos extraídos (categorías, schemas, mapas)
│   ├── clean_categories.json     # 222 categorías de Frávega
│   ├── category_map.json         # Mapeo slug → UUID
│   └── ...
│
├── output/                   # Archivos HTML generados
│   └── (reportes generados)
│
└── lab/                      # Scripts de investigación (archivados)
    ├── api_probing/              # Exploración de endpoints
    ├── category_discovery/       # Descubrimiento de categorías
    ├── schema_inspection/        # Inspección de GraphQL schema
    ├── verification/             # Verificación de queries
    └── db_migrations/            # Migraciones de DB ejecutadas
```

## 🚀 Inicio Rápido

### V2 (Recomendado - Con Stock Validation)

```bash
# 1. Iniciar el sniffer V2 (con validación de stock)
python targets/fravega/sniffer_fravega_v2.py

# 2. O correr múltiples sniffers con el bridge mejorado
python web/bridge_v2.py --sniffers fravega --versions v2

# 3. Ver alertas en consola (stdout)
# Las oportunidades confirmadas aparecen con 🚀
```

### V1 (Legacy - Solo detección de glitches)

```bash
python targets/fravega/sniffer_fravega.py
```

## 📡 Flujo del Sistema V2 (Nuevo)

```
[GraphQL API] → [Candidato: Gap >= 18%?]
                          ↓
                [Margen Odiseo: (Gap - 5%) >= 10%?]
                          ↓
            [Stock Validator (Playwright)]
                          ↓
            [OPORTUNIDAD CONFIRMADA]
                          ↓
            [DB SQLite + Alerta]
            (Telegram/Discord/WebSocket)
```

**Cambio clave:** Solo alertamos oportunidades **CONFIRMADAS** (stock real validado).

---

## 🔄 Comparación V1 vs V2

| Aspecto | V1 | V2 |
|--------|----|----|
| **Detección** | Glitches (anomalías) | Oportunidades (arbitrage) |
| **Stock** | Asumido (API) | Validado (Playwright) |
| **Margen** | No calcula | Neto (Gap - 5%) |
| **Alertas** | Potenciales | Confirmadas |
| **Falsos positivos** | Altos | Bajos |
| **Speed** | ~1s/producto | ~10-15s/producto |
| **Ideal para** | Análisis / Research | SaaS / Trading |

## 🔮 Roadmap

### ✅ Fase 1: MVP (Feb 2026)
- [x] Sniffer Frávega (API GraphQL)
- [x] Stock Validator (Playwright)
- [x] Margen Odiseo (Gap - 5%)
- [x] Bridge V2 (orquestador multi-sniffer)
- [x] Persistencia SQLite (opportunities table)
- [x] Documentación refactor (REFACTOR_V2_INTEGRATION.md)

### 🚀 Fase 2: SaaS Ready (Mar 2026)
- [ ] **Alertas push** (Telegram / WhatsApp / Discord)
- [ ] **WebSocket** (dashboard real-time)
- [ ] **Segundo target** (Cetrogar V2 / Megatone V2)
- [ ] **Comparador cross-ecommerce** (arbitrage multi-tienda)
- [ ] **Worker pool async** (5-10 Playwright workers en paralelo)
- [ ] **Railway deployment** (con env vars + Dockerfile)

### 🔮 Fase 3: Escala (Apr 2026)
- [ ] **Predictor ML** (glitch probability scores)
- [ ] **Price history analysis** (detectar tendencias)
- [ ] **User dashboard** ($30k VIP tier + $100k PRO tier)
- [ ] **API pública** (webhooks para partners)
- [ ] **Tercera/cuarta tienda** (OnCity V2 / Garbarino)

### 💎 Fase 4: Enterprise (May 2026+)
- [ ] **Multi-country expansion** (Brasil, Chile, Uruguay)
- [ ] **IA avanzada** (predicción de precios)
- [ ] **Integraciones** (accounting, CRM, logistics)
- [ ] **Mobile app** (iOS + Android)

## 📑 Documentación

| Documento | Contenido |
|---|---|
| `PROTOCOL.md` | Metodología completa, hallazgos técnicos, blueprint V4.0 |
| `PROMPTS_ARSENAL.md` | 6 módulos de prompts para hacer recon en cualquier web |
