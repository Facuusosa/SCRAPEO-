import { NextResponse } from 'next/server';
import { auth } from '@/auth';
import { stripe } from '@/lib/stripe';
import Database from 'better-sqlite3';
import path from 'path';
import fs from 'fs';

export async function GET() {
    const timestamp = new Date().toISOString();
    const services: Record<string, 'ok' | 'error' | 'unavailable'> = {
        auth: 'ok',
        stripe: 'ok',
        telegram: 'ok',
        database: 'ok',
        sniffer: 'ok'
    };

    let status: 'healthy' | 'degraded' | 'down' = 'healthy';

    // Check Auth
    try {
        const session = await auth();
        if (!session) services.auth = 'ok'; // Not logged in is okay for health, just check service
    } catch (e) {
        services.auth = 'error';
        status = 'degraded';
    }

    // Check Stripe
    try {
        await stripe.balance.retrieve();
    } catch (e) {
        services.stripe = 'error';
        status = 'degraded';
    }

    // Check Telegram
    try {
        const token = process.env.TELEGRAM_BOT_TOKEN;
        const res = await fetch(`https://api.telegram.org/bot${token}/getMe`);
        if (!res.ok) services.telegram = 'error';
    } catch (e) {
        services.telegram = 'error';
        status = 'degraded';
    }

    // Check Database
    try {
        const dbPath = path.resolve(process.cwd(), 'odiseo_users.db');
        const db = new Database(dbPath);
        db.prepare('SELECT count(*) FROM users').get();
        db.close();
    } catch (e) {
        services.database = 'error';
        status = 'down';
    }

    // Check Sniffer (Check last update in DB)
    try {
        const snifferDbPath = path.resolve(process.cwd(), '..', 'targets', 'fravega', 'fravega_monitor_v2.db');
        if (fs.existsSync(snifferDbPath)) {
            const db = new Database(snifferDbPath);
            const lastOpp: any = db.prepare('SELECT confirmed_at FROM opportunities ORDER BY confirmed_at DESC LIMIT 1').get();
            if (lastOpp) {
                const lastTime = new Date(lastOpp.confirmed_at).getTime();
                const now = Date.now();
                if (now - lastTime > 30 * 60 * 1000) { // 30 mins
                    services.sniffer = 'unavailable'; // Idle
                }
            }
            db.close();
        } else {
            services.sniffer = 'unavailable';
        }
    } catch (e) {
        services.sniffer = 'error';
    }

    return NextResponse.json({
        status,
        services,
        timestamp
    });
}
