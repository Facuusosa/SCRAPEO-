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

// Normalizar nombres para comparación cruzada
function makeMatchKey(name: string) {
    if (!name) return "";
    return name.toLowerCase()
        .replace(/[^a-z0-9]/g, "")
        .substring(0, 30);
}

export function getUnifiedProducts(category = null, search = "", limit = 500, offset = 0, isGlitchRadar = false) {
    const allProducts: any[] = [];
    const marketMap: Record<string, any[]> = {};

    // Primero: Barrido de todas las tiendas para construir un índice de mercado completo
    for (const [id, storeName] of Object.entries(STORES)) {
        const dbPath = path.join(DB_DIR, `${id}_monitor.db`);
        if (!fs.existsSync(dbPath)) continue;

        try {
            const db = new Database(dbPath, { readonly: true });

            // Detección dinámica de esquema
            const tableInfo = db.prepare("PRAGMA table_info(products)").all() as any[];
            const cols = tableInfo.map(c => c.name);
            const nameCol = cols.includes("title") ? "title" : "name";
            const priceCol = cols.includes("last_price") ? "last_price" : "current_price";
            const brandCol = cols.includes("brand_name") ? "brand_name" : "brand";
            const imgCol = cols.includes("image_url") ? "image_url" : cols.includes("image") ? "image" : "img";
            const urlCol = cols.includes("slug") ? "slug" : cols.includes("url") ? "url" : "link";

            // Query optimizada para el motor de búsqueda
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

            if (search) {
                query += ` AND (${nameCol} LIKE ? OR ${brandCol} LIKE ?)`;
                params.push(`%${search}%`, `%${search}%`);
            }

            const rows = db.prepare(query).all(...params) as any[];

            rows.forEach(r => {
                const key = makeMatchKey(r.name);
                const productWithId = { ...r, match_key: key };

                if (!marketMap[key]) marketMap[key] = [];
                marketMap[key].push(productWithId);
                allProducts.push(productWithId);
            });
            db.close();
        } catch (e) {
            console.error(`Error loading ${id}:`, e);
        }
    }

    // Segundo: Enriquecimiento y Filtrado (Arbitraje)
    const processed = allProducts.map(p => {
        const peers = marketMap[p.match_key] || [];
        const others = peers.filter(o => o.store !== p.store);
        const prices = others.map(o => o.price);
        const marketMin = prices.length > 0 ? Math.min(...prices) : null;

        const gap = marketMin ? ((marketMin - p.price) / marketMin) * 100 : 0;

        return {
            ...p,
            market_min: marketMin,
            gap: gap,
            competitors: others.map(o => ({ store: o.store, price: o.price })),
            verified: (p.discount_pct && p.discount_pct > 35) || gap > 12
        };
    });

    // Filtros finales
    let filtered = processed;
    if (isGlitchRadar) {
        filtered = processed.filter(p => (p.discount_pct && p.discount_pct > 30) || (p.gap && p.gap > 15));
    }

    if (category) {
        filtered = filtered.filter(p => p.category && String(p.category).toLowerCase().includes(String(category).toLowerCase()));
    }

    // Ordenar por relevancia (Gap > Descuento > Precio)
    return filtered
        .sort((a, b) => {
            const scoreA = (a.gap || 0) * 2 + (a.discount_pct || 0);
            const scoreB = (b.gap || 0) * 2 + (b.discount_pct || 0);
            return scoreB - scoreA;
        })
        .slice(offset, offset + limit);
}
