# 🧠 ODISEO CORE STRATEGY

Este documento centraliza la inteligencia del proyecto, uniendo los principios de **Antigravity AI** con los requerimientos de arbitraje de mercado de **Odiseo**.

## 1. Arquitectura de Datos (The Unified Ledger)
Todos los scrapers deben persistir sus datos con un esquema normalizado para permitir comparaciones instantáneas.
- **Directorio Central:** `data/databases/`
- **Naming:** `{tienda}_monitor.db`
- **Tablas Core:** `products`, `price_history`, `alerts`.

## 2. Lógica de Arbitraje (Price Match Engine)
El sistema debe identificar el mismo producto en diferentes tiendas para encontrar "Gaps" de mercado.
- **Normalización de Nombres:** Eliminar caracteres especiales, pasar a minúsculas y truncar para crear un `match_key`.
- **Detección de Oportunidad:**
    - `GAP % = ((Precio_Máximo_Mercado - Precio_Actual) / Precio_Máximo_Mercado) * 100`
    - `GLITCH:` Cualquier caída de precio > 40% respecto a su propio historial.

## 3. UI/UX Principles (Minimalist Decision Flow)
Diseñado para la toma de decisiones, no para la navegación casual.
- **Idioma:** Español Neutro (AR).
- **Estética:** Fondo blanco (`Slate-50`), tarjetas claras, tipografía legible.
- **Jerarquía:** 
    1. Ahorro Real (Precio vs Lista).
    2. Comparativa (Dónde está más barato).
    3. Acción Directa (Link a tienda).

## 4. Skills Integrados
- `analyze-prices`: Cálculo de márgenes de reventa (>15% como objetivo).
- `hunt-apis`: Búsqueda de endpoints GraphQL para mayor velocidad vs HTML Scraping.
- `debug-scraper`: Manejo de errores 403/WAF usando Ja3 Fingerprinting.

## 5. Roadmap de Funciones God-Tier
- [ ] **Comparativa de Precios:** Ver el mismo modelo en todas las tiendas participantes al seleccionar un item.
- [ ] **Filtros Avanzados:** Categoría, Rango de Precio, Porcentaje de Descuento.
- [ ] **Total Inventory:** Acceso al listado completo de +10k items con paginación optimizada.
- [ ] **Market Momentum:** Mostrar si la categoría (ej: Celulares) está bajando de precio en general.
