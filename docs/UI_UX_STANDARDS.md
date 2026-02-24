# 🧠 Constitución de Diseño y Desarrollo: ODISEO

Este documento establece las reglas estrictas de arquitectura, UI/UX y desarrollo para el ecosistema Odiseo. Cualquier nueva funcionalidad o rediseño debe cumplir con estos estándares para garantizar un producto de grado financiero, minimalista y de alta performance.

---

## 🎨 1. Estándares de UI/UX (Minimalismo de Alta Fidelidad)

### A. Jerarquía Visual y Tipografía
- **Enfoque Financiero:** La información numérica (Precios, Margen, Gap) debe ser clara y jerárquica. La "Ganancia" es la métrica reina.
- **Tipografía:** Uso estricto de fuentes sans-serif modernas (Inter/Geist). Cuerpo de texto mínimo 16px para legibilidad.
- **Color y Contraste:** Ratio de contraste mínimo de 4.5:1. Uso de colores semánticos:
  - `Emerald-500/600`: Oportunidades confirmadas (Profit).
  - `Amber-500`: Validaciones necesarias (Espejismos).
  - `Slate-900`: Texto principal y CTA primarios.

### B. Interacción y Feedback (Touch & Interaction)
- **Targets:** Todo elemento interactivo debe tener un área de clic/toque mínima de `44x44px`.
- **Estados de Carga:** Los botones deben deshabilitarse y mostrar un estado de carga (Spinner/Skeleton) durante operaciones asíncronas para evitar clics dobles.
- **Cero Salto de Contenido:** Reservar espacio para imágenes y datos asíncronos para evitar que la UI "salte" al cargar.

---

## ⚡ 2. Performance y Arquitectura (Zero-Latency Mindset)

### A. Eliminación de Waterfalls (Estrategia de Carga)
- **Paralelismo:** Usar `Promise.all()` para fetching de datos independientes (ej: leer múltiples bases de datos).
- **Streaming:** Implementar `Suspense` y `Skeleton Screens` para mostrar la estructura de la página mientras los datos viajan.
- **Lazy Loading:** Uso de `next/dynamic` para componentes pesados fuera del viewport inicial.

### B. Optimización de JavaScript
- **Búsquedas O(1):** Preferir `Map` y `Set` sobre `.find()` o `.includes()` en arrays grandes durante el proceso de matching de productos.
- **Retornos Tempranos:** Aplicar el patrón `early-exit` para reducir el nesting y mejorar la legibilidad.
- **Inmutabilidad Moderna:** Usar `.toSorted()`, `.toReversed()` para mantener el estado original limpio.

---

## 🛠️ 3. Reglas de Desarrollo (Clean Code)

### A. Componentes y State Management
- **Hoisting de JSX:** Mover JSX estático fuera de la función del componente para reducir la carga en cada re-render.
- **Inyectores de Estado (SSE):** Las actualizaciones en tiempo real vía Server-Sent Events deben inyectarse mediante un "unshift" en el estado local, garantizando una **Optimistic UI** sin parpadeos.
- **Sanitización Obligatoria:** Toda URL externa debe pasar por `sanitizeUrl` antes de ser inyectada en un `href`.

### B. Accesibilidad (A11y)
- **Iconografía:** Todo botón que solo contenga un icono debe llevar un `aria-label` descriptivo.
- **Navegación:** El orden del Tab debe coincidir siempre con el orden visual.

---

## 🚩 4. Anti-Patrones Prohibidos
- ❌ **Reload Forzado:** Prohibido el uso de `router.refresh()` o `window.location.reload()` para actualizaciones de datos.
- ❌ **Empty Buttons:** Botones sin estado `disabled` durante el fetch.
- ❌ **Hardcoded Constants:** Información de negocio (dominios, categorías) fuera de `lib/` o constantes centralizadas.

> "Odiseo no es solo una app, es una herramienta de precisión. Si el código no es preciso, el negocio no escala."
