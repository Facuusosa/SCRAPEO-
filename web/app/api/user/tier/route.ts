import { NextResponse } from "next/server";
import { auth } from "@/auth";
import Database from "better-sqlite3";
import path from "path";
import { handleApiError } from "@/lib/error-handler";
import { logger } from "@/lib/logger";

const dbPath = path.resolve(process.cwd(), "odiseo_users.db");

export async function GET() {
    const SOURCE = "API_USER_TIER";
    const session = await auth();

    if (!session?.user?.id) {
        return NextResponse.json({ error: "No autorizado" }, { status: 401 });
    }

    try {
        const db = new Database(dbPath);
        const sub = db.prepare("SELECT tier, status, expires_at FROM subscriptions WHERE user_id = ?").get(session.user.id) as any;
        db.close();

        return NextResponse.json({
            tier: sub?.tier || "free",
            status: sub?.status || "inactive",
            expiresAt: sub?.expires_at || null,
            isVip: sub?.status === 'active' && (sub?.tier === 'vip_telegram' || sub?.tier === 'mercado_pro')
        });
    } catch (error: any) {
        return handleApiError(error, SOURCE);
    }
}
