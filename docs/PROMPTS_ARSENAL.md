# 🕵️‍♂️ ARSENAL DE PROMPTS — Extracción de Inteligencia Web

> **Regla de Oro:** Nunca le pidas "inspecciona la página". Siempre dale un **objetivo de inteligencia**.

---

## Flujo de Trabajo

1. **Elegí tu objetivo** — ¿APIs? ¿Precios? ¿Sesiones? ¿Feature flags?
2. **Copiá el prompt** del módulo correspondiente
3. **Pegalo en la IA** — Te va a pedir el código fuente o tráfico de red
4. **Seguí las instrucciones** — No necesitás entender el código, solo conseguirlo
5. **Recibí el informe** — Resumen claro y accionable
6. **Iterá** — Usá la nueva info para pedir análisis más profundos

---

## Módulo 1: Mapeo de Arquitectura

**Objetivo:** Entender las tecnologías del sitio target.

```text
Agente, necesito un informe de arquitectura de [URL OBJETIVO]. Analiza el código fuente y enumera:

1. Frontend Framework (React, Vue, Angular, etc.)
2. Librerías Clave (Apollo Client, Redux, jQuery)
3. Sistema Anti-Bot/WAF (Cloudflare, Akamai, etc.)
4. Plataforma E-commerce (Magento, Shopify, VTEX, custom)
5. Herramientas de Analítica (GTM, Segment, etc.)

Para cada tecnología, describí qué implica para nuestra estrategia de monitoreo.
```

**Te va a pedir:** El HTML de la página principal (click derecho → Ver código fuente → copiar todo).

---

## Módulo 2: Caza de Endpoints de API

**Objetivo:** Encontrar todas las APIs para precios, stock, búsqueda, carrito.

```text
Agente, mapeá todos los endpoints de API de [URL OBJETIVO]. Examiná el JavaScript
y buscá patrones: fetch(', axios.post(', graphql, /api/, /v1/.

Devolveme una lista con:
1. URL del Endpoint
2. Método HTTP (GET, POST, PUT, DELETE)
3. Payload Esperado
4. Función (productos, precios, carrito, login, búsqueda)
5. Autenticación (headers, cookies, tokens)

Concentrate en APIs de productos, precios, carrito y búsqueda.
```

**Te va a pedir:** Los archivos `.js` principales (DevTools → Sources → `app.js`, `main.js`).

---

## Módulo 3: Decodificación de Lógica de Precios

**Objetivo:** Entender cómo se calculan los precios para poder predecir anomalías.

```text
Agente, descifrá la lógica de precios de [URL OBJETIVO]. En el JavaScript, buscá funciones
que calculen o modifiquen el precio final.

Prestá atención a:
- Descuentos: ¿porcentaje fijo? ¿cupón?
- Promociones bancarias: buscar 'bank', 'card', 'installments', 'discount'
- Precios dinámicos: ¿cambia según usuario, sesión o stock?
- Variables clave: precio de lista, precio con descuento, precio final

Dame un resumen de la lógica de negocio como si se lo explicaras a otro dev.
```

**Te va a pedir:** Los archivos JavaScript que contengan la lógica de la aplicación.

---

## Módulo 4: Sesiones y Tokens de Autenticación

**Objetivo:** Modelar el sistema de auth para simular un usuario logueado.

```text
Agente, modelá el sistema de autenticación de [URL OBJETIVO]. Necesito:

1. Endpoint de Login (URL exacta)
2. Credenciales Esperadas (formato del JSON)
3. Tokens generados (buscar: token, jwt, session, auth)
4. Almacenamiento (localStorage, sessionStorage, cookies)
5. Uso del Token (header Authorization: Bearer, cookie, etc.)

Dame un modelo de sesión que podamos replicar con Python (requests o curl_cffi).
```

**Te va a pedir:** Código fuente de la página de login + captura del tráfico de red al iniciar sesión (DevTools → Network → copiar como cURL).

---

## Módulo 5: Feature Flags y Configuraciones Ocultas

**Objetivo:** Encontrar interruptores que activan ofertas o funcionalidades.

```text
Agente, buscá 'feature flags' en el código de [URL OBJETIVO]. Buscá:

- localStorage.getItem('NOMBRE_DE_FLAG')
- sessionStorage.getItem('NOMBRE_DE_FLAG')
- Variables globales: window.FEATURES, window.config
- Condicionales que habiliten/deshabiliten funcionalidades

Devolveme un diccionario con cada bandera, su valor y una hipótesis de para qué sirve.
```

**Te va a pedir:** Código fuente de la página + contenido de localStorage (DevTools → Application → Local Storage).

---

## Módulo 6: Ingeniería Inversa del Carrito y Descuentos

**Objetivo:** Entender descuentos ocultos que solo aparecen en el carrito.

```text
Agente, hacé ingeniería inversa del flujo de carrito de [URL OBJETIVO].

Analizá el tráfico cuando:
1. Agrego un producto al carrito
2. Veo el carrito
3. Aplico un cupón de descuento
4. Selecciono un método de pago (para ver si cambia el precio)

Necesito:
- Endpoint del carrito (URL)
- Payload de actualización
- Lógica de descuentos (¿frontend o backend?)
- Variables de descuento (subtotal, descuento, total final)

Dame el flujo completo y los endpoints involucrados.
```

**Te va a pedir:** Las peticiones de red en formato cURL para cada acción (DevTools → Network → copiar como cURL).

---

> **Recordá:** Cada módulo alimenta al siguiente. Descubrís una API → entendés sus precios → modelás la sesión → construís el sniffer.
