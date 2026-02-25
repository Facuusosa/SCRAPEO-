import { NextResponse } from 'next/server';
import { stripe } from '@/lib/stripe';
import { headers } from 'next/headers';
import { getDbClient } from '@/lib/db-adapter';
import { logger } from '@/lib/logger';
import { handleApiError } from '@/lib/error-handler';
import { alertAdmin } from '@/lib/alert-admin';

export async function POST(req: Request) {
    const SOURCE = 'STRIPE_WEBHOOK';
    const body = await req.text();
    const signature = (await headers()).get('stripe-signature') as string;

    let event;
    try {
        event = stripe.webhooks.constructEvent(body, signature, process.env.STRIPE_WEBHOOK_SECRET!);
    } catch (err: any) {
        logger.error(SOURCE, `Firma de webhook inválida: ${err.message}`);
        return NextResponse.json({ error: `Webhook Error: ${err.message}` }, { status: 400 });
    }

    const session = event.data.object as any;
    const db = await getDbClient();

    try {
        switch (event.type) {
            case 'checkout.session.completed': {
                const userId = session.metadata.userId;
                const customerId = session.customer;
                const subscriptionId = session.subscription;
                const planId = session.metadata.planId;

                logger.info(SOURCE, `✅ Pago completado: User ${userId} | Plan ${planId}`);

                if (db.type === 'postgres') {
                    await db.execute(`
              INSERT INTO subscriptions (user_id, stripe_customer_id, stripe_subscription_id, tier, status)
              VALUES ($1, $2, $3, $4, $5)
              ON CONFLICT (user_id) DO UPDATE SET 
                stripe_customer_id = EXCLUDED.stripe_customer_id,
                stripe_subscription_id = EXCLUDED.stripe_subscription_id,
                tier = EXCLUDED.tier,
                status = EXCLUDED.status
            `, [userId, customerId, subscriptionId, planId, 'active']);
                    await db.execute(`UPDATE telegram_users SET tier = $1 WHERE user_id = $2`, [planId, userId]);
                } else {
                    // SQLite
                    await db.execute(`
              INSERT INTO subscriptions (user_id, stripe_customer_id, stripe_subscription_id, tier, status)
              VALUES (?, ?, ?, ?, ?)
              ON CONFLICT(user_id) DO UPDATE SET 
                stripe_customer_id = excluded.stripe_customer_id,
                stripe_subscription_id = excluded.stripe_subscription_id,
                tier = excluded.tier,
                status = excluded.status
            `, [userId, customerId, subscriptionId, planId, 'active']);
                    await db.execute(`UPDATE telegram_users SET tier = ? WHERE user_id = ?`, [planId, userId]);
                }

                await alertAdmin('INFO', `Nuevo suscriptor! User: ${userId} - Plan: ${planId}`);
                break;
            }

            case 'customer.subscription.deleted': {
                const subIdDeleted = session.id;
                const sub = await db.get("SELECT user_id FROM subscriptions WHERE stripe_subscription_id = $1 OR stripe_subscription_id = ?", [subIdDeleted, subIdDeleted]) as any;

                logger.warn(SOURCE, `Suscripción cancelada: ${subIdDeleted}`);

                if (db.type === 'postgres') {
                    await db.execute('UPDATE subscriptions SET status = $1, tier = $2 WHERE stripe_subscription_id = $3', ['canceled', 'free', subIdDeleted]);
                    if (sub) await db.execute('UPDATE telegram_users SET tier = $1 WHERE user_id = $2', ['free', sub.user_id]);
                } else {
                    await db.execute('UPDATE subscriptions SET status = ?, tier = ? WHERE stripe_subscription_id = ?', ['canceled', 'free', subIdDeleted]);
                    if (sub) await db.execute('UPDATE telegram_users SET tier = ? WHERE user_id = ?', ['free', sub.user_id]);
                }

                if (sub) await alertAdmin('WARN', `Suscripción cancelada para usuario ${sub.user_id}`);
                break;
            }
        }
    } catch (dbError: any) {
        await alertAdmin('CRITICAL', `Fallo crítico en Webhook DB: ${dbError.message}`);
        return handleApiError(dbError, SOURCE);
    } finally {
        await db.close();
    }

    return NextResponse.json({ received: true });
}
