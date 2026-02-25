# ☁️ GUÍA DE DEPLOYMENT: RAILWAY — ODISEO MVP

Esta guía detalla los pasos para poner Odiseo en producción utilizando **Railway**.

## 1. Preparación de la Infraestructura
1. Crea un nuevo proyecto en **Railway.app**.
2. Agrega un servicio de **PostgreSQL**.
3. Conecta tu repositorio de GitHub.

## 2. Configuración de Variables de Entorno
Copia los valores de tu `.env` local al dashboard de Railway (Sección Variables):

- `NEXT_PUBLIC_APP_URL`: `https://tu-dominio.app`
- `NEXTAUTH_URL`: `https://tu-dominio.app`
- `NEXTAUTH_SECRET`: Genera uno nuevo.
- `STRIPE_SECRET_KEY`: Usa la `sk_live` de Stripe.
- `STRIPE_WEBHOOK_SECRET`: Obtén el secreto del webhook de producción.
- `TELEGRAM_BOT_TOKEN`: El token de tu bot de producción.
- `TELEGRAM_CHAT_ID`: El ID del canal VIP.
- `TELEGRAM_ADMIN_CHAT_ID`: Tu ID para alertas de sistema.

*Nota: Railway inyectará automáticamente `DATABASE_URL`.*

## 3. Despliegue (Build & Deploy)
1. Haz un `git push origin main`.
2. Railway detectará el `Dockerfile` y comenzará el build multi-stage (Node + Python).
3. Una vez terminado, el servicio web estará en el puerto 3000.

## 4. Migración de Base de Datos
Si deseas migrar tus usuarios existentes de SQLite a Postgres:
1. Conéctate al shell de Railway o ejecuta localmente apuntando a la `DATABASE_URL` de producción:
```bash
python tools/migrate_sqlite_to_postgres.py
```

## 5. Configuración del Sniffer (Cron)
En el Dashboard de Railway:
1. Asegúrate de que el servicio `sniffer-cron` esté configurado con el comando `bash tools/run_sniffer_cron.sh`.
2. El schedule recomendado es `*/5 * * * *` (cada 5 minutos).

## 6. Monitoreo Post-Deploy
Ejecuta el script de validación externa:
```bash
bash tools/post_deploy_check.sh https://tu-dominio.app
```

---
*Odiseo v2.0 - Production Readiness*
