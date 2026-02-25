import { logger } from './logger';

/**
 * Reintenta una función asíncrona con backoff exponencial.
 */
export async function retryWithBackoff<T>(
    fn: () => Promise<T>,
    maxRetries = 3,
    initialDelay = 1000,
    source = 'RETRY_SYSTEM'
): Promise<T> {
    let lastError: any;
    let delay = initialDelay;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            return await fn();
        } catch (error: any) {
            lastError = error;
            logger.warn(source, `Fallo en intento ${attempt}/${maxRetries}. Reintentando en ${delay}ms...`, { error: error.message });

            if (attempt < maxRetries) {
                await new Promise(resolve => setTimeout(resolve, delay));
                delay *= 2; // Exponencial backoff
            }
        }
    }

    logger.error(source, `Todos los reintentos (${maxRetries}) han fallado.`, { error: lastError?.message });
    throw lastError;
}
