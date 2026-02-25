# 🧠 ODISEO: Technical & Business Master Briefing
**Versión:** 2.0 (Feb 2026)  
**Clasificación:** Confidencial / Fuente NotebookLM  
**Propósito:** Documento de referencia para el modelo de negocio e infraestructura técnica del ecosistema Odiseo.

---

## 🛠️ 1. Stack Tecnológico (Infraestructura de Grado Financiero)

Odiseo está construido bajo la premisa de la **"Constitución de Diseño y Desarrollo"**, priorizando el minimalismo de alta fidelidad y la eliminación total de latencia.

*   **Frontend:** Next.js 15 (App Router) y React 19. Implementación de *Streaming SSR* y *Suspense* para evitar parpadeos de UI.
*   **Styling:** Tailwind CSS siguiendo un sistema de tokens estrictos:
    *   `Emerald-500/600` para Rentabilidad Confirmada.
    *   `Slate-900` para legibilidad financiera.
    *   Layouts resilientes con grillas adaptativas (Grid/Flexbox) y sidebars colapsables.
*   **Backend:** Next.js API Routes (Node.js) con integración nativa con SQLite para velocidad de consulta O(1).
*   **Real-Time:** Implementación de **Server-Sent Events (SSE)** vía `/api/events` para inyección de oportunidades en vivo sin recarga de página (Optimistic UI).
*   **Data Ingestion:** Scrapers políglotas (Python/Playwright) que operan en segundo plano, comunicándose mediante un `bridge.py` para alimentar la base de datos centralizada.

---

## 🛰️ 2. Lógica de Negocio: Arbitraje de Precios

El núcleo de Odiseo es la detección de **ineficiencias en el mercado retail argentino**.

*   **Retailers Monitoreados:** 6 gigantes del mercado (Frávega, Cetrogar, Megatone, Musimundo, OnCity, Naldo).
*   **El Algoritmo de Gap:**
    1.  **Captura:** Extracción de SKU, Marca y Precio de la Tienda A.
    2.  **Matching:** Búsqueda cruzada en la base de datos unificada utilizando normalización de strings.
    3.  **Cálculo de Brecha:** `Gap = (Precio_Mínimo_Mercado - Precio_Tienda_A)`.
    4.  **Validación de Oportunidad:** Si el `Margen a favor` es superior al 15%, el producto se etiqueta como **"Oportunidad Confirmada"**.
*   **Conceptos de Usuario:** Reemplazo de jerga técnica por términos de negocio:
    *   *Profit* ➔ **Margen a favor**.
    *   *ROI* ➔ **Diferencia vs Mercado**.

---

## 📊 3. Estructura de Datos y APIs

El ecosistema se organiza en torno a un flujo de datos limpio y estructurado:

*   **`clean_categories.json`:** Una lista maestra unificada de más de 200 categorías agrupadas jerárquicamente. Permite al motor de búsqueda normalizar productos de diferentes tiendas (ej: "Laptops" vs "Notebooks") en un solo nicho.
*   **API Market Pro:**
    *   `/api/products`: Devuelve el catálogo unificado con filtros reactivos por precio, tienda y margen.
    *   `/api/telegram-feed`: Un sub-set de datos pre-filtrados (Margen > 15%) listo para ser consumido por bots de alertas automatizadas. El formato está optimizado para baja transferencia de datos (JSON ligero).
*   **Desinfectante de URLs:** Sistema `sanitizeUrl` que garantiza que los links de afiliados y compra sean siempre absolutos y libres de redirecciones circulares del WAF.

---

## 💰 4. Modelo de Monetización: La Escalera de Valor

Odiseo trasciende el ser una herramienta para convertirse en un **modelo de negocio recurrente (SaaS)**.

### A. Canal VIP de Alertas (Entry Level) - **$30.000 ARS/mes**
*   **Entrega:** Acceso a un canal de Telegram privado.
*   **Valor:** Alertas en tiempo real de los "Glitches" (errores de sistema) y ofertas agresivas.
*   **Público:** Revendedores individuales y buscadores de ofertas.

### B. Licencia Web PRO (Professional Tier) - **$100.000 ARS/mes**
*   **Entrega:** Credenciales de acceso al dashboard **Mercado Pro**.
*   **Valor:** 
    *   Acceso a los 5.000+ productos monitoreados.
    *   Filtros tácticos avanzados (Margen exacto, rango de inversión).
    *   Comparador de precios entre las 6 tiendas en una sola pantalla.
*   **Público:** Inversores de arbitraje, dueños de locales de tecnología y "flippers" profesionales.

---

## 📈 5. Visión de Escalabilidad

1.  **Nacional:** Inclusión de retailers de nicho (especialistas en computación o electro).
2.  **Tecnológica:** Implementación de *Fuzzy Matching* avanzado para reducir falsos positivos en marcas blancas.
3.  **Horizontal:** Expansión del modelo de arbitraje a otros verticales (Vuelos vía Flybondi, Neumáticos, etc.).

> "Odiseo no predice el mercado, lo explota en tiempo real."
