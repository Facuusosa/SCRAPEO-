import Database from "better-sqlite3";
import path from "path";
import fs from "fs";

// Mapeo de bases de datos
const ROOT_DIR = path.resolve(process.cwd(), "..");
const DB_DIR = path.join(ROOT_DIR, "data", "databases");

const STORES = {
    fravega: "Fravega",
    oncity: "OnCity",
    cetrogar: "Cetrogar",
    megatone: "Megatone",
    newsan: "Newsan",
    casadelaudio: "Casa del Audio"
};

/**
 * 🧠 MOTOR DE MATCHING SEMÁNTICO V2
 */
function makeSemanticKey(name: string) {
    if (!name) return "";
    let key = name.toLowerCase();
    const noise = ["celular", "smartphone", "smart", "tv", "led", "oled", "pulgadas", "monitor", "notebook"];
    const noiseRegex = new RegExp(`\\b(${noise.join("|")})\\b`, "gi");
    key = key.replace(noiseRegex, "").replace(/[^a-z0-9 ]/g, " ");
    const tokens = key.split(/\s+/).filter(t => t.length > 1);
    return tokens.sort().join("");
}

export function getUnifiedProducts(category = null, search = "", limit = 500, offset = 0, isGlitchRadar = false) {
    const allProducts: any[] = [];
    const marketMap: Record<string, any[]> = {};

    for (const [id, storeName] of Object.entries(STORES)) {
        const dbPath = path.join(DB_DIR, `${id}_monitor.db`);
        if (!fs.existsSync(dbPath)) continue;

        try {
            const db = new Database(dbPath, { readonly: true });
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
