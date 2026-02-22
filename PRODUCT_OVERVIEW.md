# 🇦🇷 AR Monitor v1.0: Sistema de Inteligencia de Mercado

Este documento detalla la infraestructura, capacidades y potencial de negocio del sistema de monitoreo de e-commerce desarrollado.

---

## 1. Cobertura de Mercado (Targets)
Hemos logrado hackear y automatizar la extracción de datos de los **6 gigantes del retail en Argentina**, cubriendo más del 80% del tráfico de electro y tecnología:

| Target | Técnica | Estabilidad | Descripción |
| :--- | :--- | :--- | :--- |
| **Frávega** | API GraphQL | Alta | Conexión directa a su motor de búsqueda interno. |
| **Cetrogar** | API GraphQL | Alta | Extracción masiva vía Magento 2 GQL. |
| **On City** | API VTEX | Alta | Integración con el sistema de inventario VTEX. |
| **Megatone** | API Doofinder | Extrema | Usa el buscador externo de Megatone; es el más rápido. |
| **Newsan** | HTML Ninja | Media | Bypass de WAF mediante clonación de sesión real. |
| **Casa del Audio** | HTML Ninja | Media | Extracción directa del DOM con cookies de sesión. |

---

## 2. Cómo funciona la tecnología
El sistema está construido con un enfoque **industrial y sigiloso**:

1.  **Core Robusto (`BaseSniffer`)**: Una clase maestra que garantiza que todos los scrapers sigan las mismas reglas (extraer nombre, precio, marca, link, imagen y stock).
2.  **HttpClient Stealth**: El motor de peticiones utiliza `curl_cffi` para **imitar navegadores reales** (Chrome 144), rotando headers y manejando cookies para evitar bloqueos por cortafuegos (WAF).
3.  **Persistencia Inteligente**: Bases de datos SQLite locales que permiten:
    *   Historial de precios (para ver si un descuento es real o inflado).
    *   Detección de **Glitches** (errores de sistema o precios absurdamente bajos).
    *   Análisis de stock.

---

## 3. Capacidades de Toma de Decisión
Este producto no es un simple scraper; es una herramienta de **arbitraje y análisis**:

*   **Detección de Oportunidades**: Scripts como `scan_megatone_deep.py` analizan el margen de ganancia real y el porcentaje de descuento vs el promedio histórico.
*   **Super Buscador**: Permite comparar un mismo SKU (ej: Samsung S24) en todas las tiendas en 1 segundo.
*   **Gestión de Glitches**: Alertas inmediatas cuando un precio cae por debajo del costo (ideal para reventa).

---

## 4. Estrategia de Venta y Escalamiento
Para convertir esto en un producto comercializable o una herramienta de inversión profesional:

### Paso A: Automatización (Próximamente)
*   **Cloud Deployment**: Mover los sniffers a un servidor (VPS/Docker) para que corran 24/7.
*   **Telegram Bot**: Enviar alertas instantáneas de "PRECIO BOMBA" directamente al celular.

### Paso B: El Producto Final (Monetización)
1.  **Modelo de Arbitraje**: Usarlo nosotros para comprar barato y revender oficial/privadamente.
2.  **SaaS para Marcas**: Venderle a marcas (ej: Philips, Samsung) un reporte diario de a cuánto están vendiendo sus productos los retailers.
3.  **Comparador Premium**: Crear una plataforma donde el usuario paga por ver "Glitches Reales" antes que nadie.

---

## 5. Próximos Pasos Técnicos
1.  **Refinar Atributos**: Extraer más detalles (cuotas sin interés, envío gratis).
2.  **Frontend**: Crear un Dashboard visual (Next.js) para ver las curvas de precios en lugar de ver código.
3.  **Integración de IA**: Usar modelos de lenguaje para clasificar categorías automáticamente y detectar ofertas engañosas ("subieron el precio antes de descontarlo").

---
**Estado Actual:** Escaneo Maestro Iniciado (Recuperando ~20,000 puntos de datos).
