import { NextResponse } from 'next/server';
import { stripe } from '@/lib/stripe';
import { auth } from '@/auth';
import { logger } from '@/lib/logger';
import { handleApiError } from '@/lib/error-handler';
import { retryWithBackoff } from '@/lib/retry';

export async function POST(req: Request) {
    const SOURCE = 'API_CHECKOUT';
    try {
        const session_auth = await auth();
        const { planId } = await req.json();

        if (!session_auth?.user?.id) {
            logger.warn(SOURCE, 'Intento de checkout sin sesión activa.');
            return NextResponse.json({ error: 'No autorizado' }, { status: 401 });
        }

        if (!planId) {
            return NextResponse.json({ error: 'Plan ID es requerido' }, { status: 400 });
        }

        logger.info(SOURCE, `Iniciando checkout para usuario ${session_auth.user.id}, plan: ${planId}`);

        const prices: Record<string, string | undefined> = {
            'vip_telegram': process.env.STRIPE_PRICE_VIP,
            'mercado_pro': process.env.STRIPE_PRICE_PRO,
        };

        const priceId = prices[planId];
        if (!priceId) {
            logger.error(SOURCE, `Configuración faltante: No hay PriceID definido para ${planId}`);
            return NextResponse.json({ error: 'Plan o precio no configurado' }, { status: 400 });
        }

        // Usar Retry para llamadas externas a Stripe
        const checkoutSession = await retryWithBackoff(() =>
            stripe.checkout.sessions.create({
                payment_method_types: ['card'],
                line_items: [{ price: priceId, quantity: 1 }],
                mode: 'subscription',
                success_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard?success=true&session_id={CHECKOUT_SESSION_ID}`,
                cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/pricing?canceled=true`,
                metadata: {
                    userId: session_auth.user.id!,
                    planId,
                },
                customer_email: session_auth.user.email || undefined,
            }),
            3, 1000, SOURCE
        );

        logger.info(SOURCE, `Sesión de checkout creada: ${checkoutSession.id}`);

        return NextResponse.json({ url: checkoutSession.url });
    } catch (error: any) {
        return handleApiError(error, SOURCE);
    }
}
