# 🛡️ PROTOCOLO DE ROBUSTEZ Y ERRORES — ODISEO MVP

Este sistema está diseñado para ser resiliente a fallos externos (Stripe, Telegram, WAF) y asegurar que el usuario nunca pierda su acceso sin notificación.

## 🗒️ Sistema de Logs

Los logs se centralizan en `web/logs/app.log`. Cada entrada sigue el formato:
`[TIMESTAMP] [LEVEL] [SOURCE] MESSAGE | Data: {json}`

### Niveles
- `INFO`: Flujos normales (login, pago iniciado).
- `WARN`: Anomalías recuperables (reintento de Stripe, bot ocupado).
- `ERROR`: Fallos críticos que requieren atención inmediata.

---

## 🔄 Lógica de Reintentos (Backoff)

Para operaciones críticas con APIs externas, usamos `retryWithBackoff`:
1. **Intento 1**: Inmediato.
2. **Intento 2**: Espera 2s.
3. **Intento 3**: Espera 4s.

Si después de 3 intentos persiste el error, se notifica al Administrador.

---

## 🛰️ Health Check (`/api/health`)

Endpoint para monitoreo externo (ej. UptimeRobot). Devuelve 200 siempre que el sistema base funcione, pero indica estados degradados:
- `HEALTHY`: Todo operativo.
- `DEGRADED`: Algún servicio externo (Stripe/Telegram) falla pero la DB está ok.
- `DOWN`: Base de datos inaccesible.

---

## 🚨 Alertas Administrativas

Si ocurre un error crítico (ej. Webhook de Stripe falla), el sistema envía una alerta inmediata al Administrador vía Telegram indicando la fuente y el error detallado.

---

## 🐍 Resiliencia del Sniffer

El script `scrapers/error_resilience.py` actúa como un "guardian":
- Si el sniffer crashea por un cambio de HTML o red, el guardian lo detecta.
- Realiza hasta 5 reintentos con esperas incrementales.
- Loguea el error detallado para que el dev pueda corregir el target.

---
*Odiseo v2.0 - Resilience Core*
