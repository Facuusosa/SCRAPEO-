import { logger } from './logger';

export async function getDbClient() {
    if (process.env.DATABASE_URL) {
        const { Pool } = await import('pg');
        const pool = new Pool({ connectionString: process.env.DATABASE_URL });

        return {
            type: 'postgres',
            query: async (text: string, params?: any[]) => {
                const res = await pool.query(text, params);
                return res.rows;
            },
            execute: async (text: string, params?: any[]) => {
                return await pool.query(text, params);
            },
            get: async (text: string, params?: any[]) => {
                const res = await pool.query(text, params);
                return res.rows[0];
            },
            close: async () => await pool.end()
        };
    } else {
        const Database = (await import('better-sqlite3')).default;
        const path = await import('path');
        const db = new Database(path.resolve(process.cwd(), "odiseo_users.db"));

        return {
            type: 'sqlite',
            query: async (text: string, params: any[] = []) => {
                // Convert $1, $2 to ? for sqlite if needed, but better to use ? in code
                return db.prepare(text).all(...params);
            },
            execute: async (text: string, params: any[] = []) => {
                return db.prepare(text).run(...params);
            },
            get: async (text: string, params: any[] = []) => {
                return db.prepare(text).get(...params);
            },
            transaction: (fn: Function) => {
                return db.transaction(fn as any)();
            },
            close: async () => db.close()
        };
    }
}
