import { NextResponse } from 'next/server';
import { logger } from './logger';
import { alertAdmin } from './alert-admin';

export async function handleApiError(error: any, source: string) {
    logger.error(source, `Error capturado: ${error.message}`, { stack: error.stack });

    // Stripe Errors
    if (error.type?.startsWith('Stripe')) {
        logger.warn(source, 'Stripe API Error detectado.', { type: error.type });

        if (error.type === 'StripeConnectionError') {
            return NextResponse.json(
                { error: 'Error de conexión con el proveedor de pagos. Reintentando automáticamente...' },
                { status: 503 }
            );
        }

        // Alerta admin si es un error de configuración o cuenta
        if (error.type === 'StripeAuthenticationError' || error.type === 'StripeInvalidRequestError') {
            await alertAdmin('CRITICAL', `Error de Stripe en ${source}: ${error.message}`);
        }

        return NextResponse.json(
            { error: 'Hubo un problema procesando el pago. Por favor intenta de nuevo.' },
            { status: 400 }
        );
    }

    // Database Errors (Better-SQLite3)
    if (error.message?.includes('database is locked') || error.code === 'SQLITE_BUSY') {
        logger.warn(source, 'Database is locked, transaction probably aborted.');
        return NextResponse.json({ error: 'Sistema ocupado, reintentando...' }, { status: 503 });
    }

    // Fallback
    await alertAdmin('WARN', `Error no controlado en ${source}: ${error.message}`);
    return NextResponse.json(
        { error: 'Error interno del servidor.' },
        { status: 500 }
    );
}
