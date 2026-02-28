# 🏛️ ODISEO — Monitor de Precios E-commerce (Argentina)

**Odiseo** es un sistema inteligente que escanea tiendas online (Frávega, Cetrogar, etc.) en busca de errores de precio (glitches) y oportunidades de reventa en tiempo real.

---

## 🚀 Cómo empezar (Guía Rápida)

Si no sabés nada de programación, seguí estos pasos para ponerlo en marcha:

### 1. Requisitos previos
- **Python 3.10+**: Para el motor de búsqueda (Scrapers).
- **Node.js**: Para ver el panel visual (Dashboard).

### 2. Instalación
Abrí una terminal en la carpeta del proyecto y ejecutá:
```bash
# Instalar dependencias del motor
pip install -r requirements.txt

# Instalar dependencias de la web
cd web
npm install
cd ..
```

### 3. Arrancar el Sistema (3 Terminales)
Para que todo funcione, te recomendamos abrir 3 terminales separadas:

*   **Terminal 1 (Dashboard):** Para ver la web.
    ```bash
    cd web
    npm run dev
    ```
*   **Terminal 2 (Puente de Datos):** Conecta los motores con la web.
    ```bash
    python web/bridge_v2.py --sniffers fravega
    ```
*   **Terminal 3 (Motor de Búsqueda):** Empieza a buscar ofertas.
    ```bash
    python targets/fravega/sniffer_fravega_v2.py
    ```

---

## 📁 Estructura del Proyecto (Versión Simple)

Para que sepas dónde está cada cosa:
- `targets/`: Contiene los motores de búsqueda para cada tienda (Frávega, Cetrogar, etc.).
- `web/`: Todo lo relacionado con la página web y el panel visual.
- `core/`: El "cerebro" compartido que usan todos los motores.
- `docs/`: Documentación técnica detallada y manuales.
- `data/`: Archivos de configuración y mapeo de categorías.

---

## 📡 ¿Cómo funciona?
1. El **Motor** (Terminal 3) revisa miles de productos por minuto.
2. Si encuentra algo barato, el **Validador** entra a la web (como un humano) para confirmar que hay stock.
3. El **Puente** (Terminal 2) envía la confirmación al **Dashboard** (Terminal 1).
4. Vos recibís el aviso y el link para comprar. 🚀

---

## 📑 Documentación Adicional
Si querés profundizar, revisá la carpeta `docs/` o leé:
- `PROTOCOL.md`: Cómo detectamos las ofertas.
- `CORE_STRATEGY.md`: La visión técnica del proyecto.
- `AGENTS.md`: Guía para desarrolladores IA.
