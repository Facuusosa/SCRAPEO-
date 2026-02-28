import Database from "better-sqlite3";
import path from "path";
import fs from "fs";

// Mapeo de bases de datos
const CWD = process.cwd();
const ROOT_DIR = CWD.endsWith('web') ? path.resolve(CWD, "..") : CWD;
const DB_DIR = path.join(ROOT_DIR, "data", "databases");

const STORES = {
    fravega: {
        name: "Fravega",
        paths: [
            "targets/fravega/fravega_monitor_v2.db",
            "targets/fravega/fravega_monitor.db",
            "data/databases/fravega_monitor.db"
        ]
    },
    oncity: {
        name: "OnCity",
        paths: [
            "oncity_monitor.db",
            "data/databases/oncity_monitor.db"
        ]
    },
    cetrogar: {
        name: "Cetrogar",
        paths: [
            "cetrogar_monitor.db",
            "data/databases/cetrogar_monitor.db"
        ]
    },
    megatone: {
        name: "Megatone",
        paths: [
            "megatone_monitor.db",
            "data/databases/megatone_monitor.db"
        ]
    },
    newsan: {
        name: "Newsan",
        paths: [
            "newsan_monitor.db",
            "data/databases/newsan_monitor.db"
        ]
    },
    casadelaudio: {
        name: "Casa del Audio",
        paths: [
            "casadelaudio_monitor.db",
            "data/databases/casadelaudio_monitor.db"
        ]
    }
};

/**
 * 🧠 MOTOR DE MATCHING SEMÁNTICO V2
 */
function makeSemanticKey(name: string) {
    if (!name) return "null_key_" + Math.random();
    let key = name.toLowerCase();

    // 1. Limpieza de ruido comercial (solo palabras muy genéricas)
    const noise = ["celular", "smartphone", "smart", "tv", "led", "oled", "pulgadas", "monitor", "notebook", "nuevo", "oferta"];
    const noiseRegex = new RegExp(`\\b(${noise.join("|")})\\b`, "gi");
    key = key.replace(noiseRegex, " ");

    // 2. Extraer modelo (Letras + Números es clave en tech)
    // Ej: "G34", "S23", "A54", "12GB", "256GB"
    const modelParts = key.match(/[a-z0-9]{2,}/g) || [];

    if (modelParts.length < 2) {
        // Si el nombre es muy corto, no arriesgamos matching: usamos el nombre completo sanitizado
        return name.toLowerCase().replace(/[^a-z0-9]/g, "");
    }

    return modelParts.sort().join("");
}

export function getUnifiedProducts(category = null, search = "", limit = 500, offset = 0, isGlitchRadar = false) {
    const allProducts: any[] = [];
    const marketMap: Record<string, any[]> = {};

    for (const [id, config] of Object.entries(STORES)) {
        let dbPath = "";

        // Buscar el primer path que exista
        for (const p of (config as any).paths) {
            const fullPath = path.resolve(ROOT_DIR, p);
            if (fs.existsSync(fullPath)) {
                const stats = fs.statSync(fullPath);
                if (stats.size > 10000) {
                    dbPath = fullPath;
                    break;
                }
            }
        }

        if (!dbPath) continue;
        const storeName = (config as any).name;

        try {
            const db = new Database(dbPath, { readonly: true });
            // db.pragma("journal_mode = WAL");
            const tableInfo = db.prepare("PRAGMA table_info(products)").all() as any[];
            const cols = tableInfo.map(c => c.name);

            const nameCol = cols.includes("title") ? "title" : "name";
            const priceCol = cols.includes("last_price") ? "last_price" : "current_price";
            const brandCol = cols.includes("brand_name") ? "brand_name" : "brand";
            const imgCol = cols.includes("image_url") ? "image_url" : cols.includes("image") ? "image" : "img";
            const urlCol = cols.includes("slug") ? "slug" : cols.includes("url") ? "url" : "link";

            let query = `
                SELECT 
                    ${nameCol} as name, 
                    ${priceCol} as price, 
                    list_price, 
                    discount_pct, 
                    ${brandCol} as brand, 
                    ${imgCol} as img, 
                    ${urlCol} as url, 
                    category,
                    '${storeName}' as store 
                FROM products 
                WHERE ${priceCol} > 500
            `;

            const params: any[] = [];

            // PRIORITY 2: Filtro de Categoría Fuzzy
            if (category && category !== "all") {
                query += ` AND (category LIKE ? OR name LIKE ?)`;
                params.push(`%${category}%`, `%${category}%`);
            }

            if (search) {
                query += ` AND (${nameCol} LIKE ? OR ${brandCol} LIKE ?)`;
                params.push(`%${search}%`, `%${search}%`);
            }

            const rows = db.prepare(query).all(...params) as any[];

            rows.forEach(r => {
                const key = makeSemanticKey(r.name);
                const productWithId = { ...r, match_key: key };

                if (!marketMap[key]) marketMap[key] = [];
                marketMap[key].push(productWithId);
                allProducts.push(productWithId);
            });
            db.close();
        } catch (e) { }
    }

    const processed = allProducts.map(p => {
        const peers = marketMap[p.match_key] || [];
        const others = peers.filter(o => o.store !== p.store);
        const prices = others.map(o => o.price);

        const marketMin = prices.length > 0 ? Math.min(...prices) : null;
        const gap = marketMin ? ((marketMin - p.price) / marketMin) * 100 : 0;

        return {
            ...p,
            market_min: marketMin,
            gap_market: gap,
            // PRIORITY 1: Pasar URL para comprobación
            competitors: others.map(o => ({ store: o.store, price: o.price, url: o.url })),
            confidence: peers.length > 1 ? "ALTA" : "MUESTREO"
        };
    });

    let filtered = processed;
    if (isGlitchRadar) {
        filtered = filtered.filter(p => p.gap_market > 15 || p.discount_pct > 30);
    }

    return filtered
        .sort((a, b) => (b.gap_market * 1.5 + b.discount_pct) - (a.gap_market * 1.5 + a.discount_pct))
        .slice(offset, offset + limit);
}
