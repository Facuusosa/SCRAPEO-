import { NextResponse } from "next/server";
import { logger } from "@/lib/logger";
import { handleApiError } from "@/lib/error-handler";
import bcrypt from "bcryptjs";
import { v4 as uuidv4 } from "uuid";

// Adaptador de DB Híbrido (SQLite para local, Postgres para Prod)
async function getDb() {
    if (process.env.DATABASE_URL) {
        const { Pool } = await import('pg');
        return new Pool({ connectionString: process.env.DATABASE_URL });
    } else {
        const Database = (await import('better-sqlite3')).default;
        const path = await import('path');
        return new Database(path.resolve(process.cwd(), "odiseo_users.db"));
    }
}

export async function POST(req: Request) {
    const SOURCE = "API_AUTH_SIGNUP";
    try {
        const { email, password } = await req.json();
        if (!email || !password) return NextResponse.json({ error: "Email y password requeridos" }, { status: 400 });

        logger.info(SOURCE, `Intento de registro: ${email}`);
        const db: any = await getDb();

        const userId = uuidv4();
        const passwordHash = await bcrypt.hash(password, 10);

        if (process.env.DATABASE_URL) {
            // Postgres Logic
            const res = await db.query("SELECT id FROM users WHERE email = $1", [email]);
            if (res.rows.length > 0) return NextResponse.json({ error: "El usuario ya existe" }, { status: 400 });

            await db.query("BEGIN");
            await db.query("INSERT INTO users (id, email, password_hash) VALUES ($1, $2, $3)", [userId, email, passwordHash]);
            await db.query("INSERT INTO subscriptions (user_id, status, tier) VALUES ($1, $2, $3)", [userId, "inactive", "free"]);
            await db.query("COMMIT");
            await db.end();
        } else {
            // SQLite Logic
            const existingUser = db.prepare("SELECT id FROM users WHERE email = ?").get(email);
            if (existingUser) return NextResponse.json({ error: "El usuario ya existe" }, { status: 400 });

            const trans = db.transaction(() => {
                db.prepare("INSERT INTO users (id, email, password_hash) VALUES (?, ?, ?)").run(userId, email, passwordHash);
                db.prepare("INSERT INTO subscriptions (user_id, status, tier) VALUES (?, ?, ?)").run(userId, "inactive", "free");
            });
            trans();
            db.close();
        }

        logger.info(SOURCE, `Registro exitoso para ${email}`);
        return NextResponse.json({ success: true, userId }, { status: 201 });

    } catch (error: any) {
        return handleApiError(error, SOURCE);
    }
}
