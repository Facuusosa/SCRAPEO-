import { logger } from './logger';

const ADMIN_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const ADMIN_CHAT_ID = process.env.TELEGRAM_ADMIN_CHAT_ID || process.env.TELEGRAM_CHAT_ID;

/**
 * Notifica errores críticos al administrador vía Telegram.
 */
export async function alertAdmin(level: 'CRITICAL' | 'WARN' | 'INFO', message: string, data?: any) {
    const fullMessage = `⚠️ **ODISEO ALERT [${level}]**\n\n${message}\n\n${data ? `\`\`\`json\n${JSON.stringify(data, null, 2)}\n\`\`\`` : ''}`;

    logger.info('ALERT_ADMIN', `Enviando alerta: ${message}`);

    if (!ADMIN_BOT_TOKEN || !ADMIN_CHAT_ID) {
        logger.warn('ALERT_ADMIN', 'Variables de telegram admin no configuradas para alertas.');
        return;
    }

    const url = `https://api.telegram.org/bot${ADMIN_BOT_TOKEN}/sendMessage`;

    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                chat_id: ADMIN_CHAT_ID,
                text: fullMessage,
                parse_mode: 'Markdown',
            }),
        });

        if (!res.ok) {
            logger.error('ALERT_ADMIN', `Fallo al enviar alerta a Telegram: ${res.status}`);
        }
    } catch (error: any) {
        logger.error('ALERT_ADMIN', `Excepción enviando alerta: ${error.message}`);
    }
}
