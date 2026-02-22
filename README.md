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

```bash
# 1. Iniciar el monitoreo de Frávega
python targets/fravega/sniffer_fravega.py

# 2. Ver alertas en consola
python tools/dashboard.py

# 3. Generar reporte HTML
python tools/generate_report.py
```

## 📡 Flujo del Sistema

```
[API Target] → [Sniffer] → [Detección de Anomalías] → [DB SQLite]
                                    ↓
                            [¿Es un glitch?]
                              /         \
                           Sí            No
                           ↓              ↓
                     [ALERTA]        [Guardar dato]
                     (Telegram/WA)    (histórico)
```

## 🔮 Roadmap

- [x] Sniffer Frávega (API GraphQL)
- [x] Detección de glitches (heurísticas)
- [x] Persistencia SQLite
- [x] Dashboard + Reportes HTML
- [ ] **Alertas push** (Telegram / WhatsApp)
- [ ] **Módulo core compartido** (base_sniffer abstracto)
- [ ] **Segundo target** (MercadoLibre / Garbarino)
- [ ] **Comparador cross-ecommerce** (mismo producto, distintos e-commerce)
- [ ] **Evasión avanzada** (JA3 / curl_cffi)
- [ ] **Verifier** (Playwright, validación en carrito real)
- [ ] **Docker** (deploy 24/7 en la nube)

## 📑 Documentación

| Documento | Contenido |
|---|---|
| `PROTOCOL.md` | Metodología completa, hallazgos técnicos, blueprint V4.0 |
| `PROMPTS_ARSENAL.md` | 6 módulos de prompts para hacer recon en cualquier web |
