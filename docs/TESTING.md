# 🧪 PROTOCOLO DE TESTING — ODISEO MVP

Este documento describe cómo validar la integridad del sistema antes de un deployment.

## 🏁 Cómo correr los tests

Desde la raíz del proyecto, ejecuta el runner maestro:

```bash
# Ejecutar con Bash
bash tools/run_tests.sh
```

### Requisitos previos
- **Python 3.10+**: Instalado y con `curl_cffi`.
- **Node.js 18+**: Para correr los tests de `web/`.
- **Variables de entorno**: Se recomienda tener configurado el `.env` (ver `.env.example`).

---

## 🛰️ Módulos de Test

### 1. Telegram (`/tools/test_telegram.py`)
- **Propósito**: Verificar que el bot está vivo, que puede enviar alertas a canales VIP y que la base de datos local persiste.
- **Qué esperar**: Un mensaje de prueba en el canal de Telegram si las credenciales son correctas.

### 2. Stripe (`/web/tests/stripe.test.ts`)
- **Propósito**: Validar la lógica de generación de planes y el procesamiento de la metadata del webhook.
- **Qué esperar**: Validación de los IDs de precio y simulación de éxito de pago.

### 3. Auth (`/web/tests/auth.test.ts`)
- **Propósito**: Verificar que el sistema de autenticación rechace datos inválidos y proteja las rutas.
- **Qué esperar**: Validación de esquemas de signup.

### 4. Landing (`/web/tests/landing.test.ts`)
- **Propósito**: Asegurar que todos los botones de acción (CTA) apunten a las URLs correctas.
- **Qué esperar**: Escaneo de enlaces internos.

---

## ❌ Solución de Problemas

- **Si falla Telegram**: Revisa `TELEGRAM_BOT_TOKEN`. Asegúrate de haberle hablado al bot primero para que el chat exista.
- **Si falla Stripe**: Revisa que los `STRIPE_PRICE_ID` coincidan con los de tu Dashboard de Stripe.
- **Si falla Auth**: Revisa la conexión con `odiseo_users.db`.

---
*Odiseo v2.0 - Testing Intelligence Core*
