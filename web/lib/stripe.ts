import Stripe from 'stripe';

if (!process.env.STRIPE_SECRET_KEY) {
    throw new Error('STRIPE_SECRET_KEY is not defined in environment variables');
}

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
    apiVersion: '2025-02-24.acacia', // Latest stable API version
});

export const PLANS = {
    VIP_TELEGRAM: {
        id: 'vip_telegram',
        name: 'Canal VIP Telegram',
        price: 30000,
        currency: 'ars',
        description: 'Alertas en tiempo real de glitches y ofertas bomba.',
    },
    MERCADO_PRO: {
        id: 'mercado_pro',
        name: 'Mercado Pro Dashboard',
        price: 100000,
        currency: 'ars',
        description: 'Acceso total al dashboard profesional con filtros tácticos.',
    },
};
