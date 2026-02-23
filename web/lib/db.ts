import Database from "better-sqlite3";
import path from "path";

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

export function getUnifiedProducts(category = null, search = "", limit = 100, offset = 0) {
    const allProducts: any[] = [];
    const marketMap: Record<string, any[]> = {};

    for (const [id, name] of Object.entries(STORES)) {
        const dbPath = path.join(DB_DIR, `${id}_monitor.db`);
        try {
            const db = new Database(dbPath, { readonly: true });

            // Obtener columnas para manejar diferencias de esquema
            const tableInfo = db.prepare("PRAGMA table_info(products)").all() as any[];
            const cols = tableInfo.map(c => c.name);

            const nameCol = cols.includes("title") ? "title" : "name";
            const brandCol = cols.includes("brand_name") ? "brand_name" : "brand";
            const priceCol = cols.includes("last_price") ? "last_price" : "current_price";
            const urlCol = cols.includes("slug") ? "slug" : "url";
            const imgCol = cols.includes("image_url") ? "image_url" : "image";

            let query = `
        SELECT 
          ${nameCol} as name, 
          ${brandCol} as brand, 
          ${priceCol} as price, 
          list_price, 
          discount_pct, 
          ${urlCol} as url, 
          ${imgCol} as img,
          category,
          '${name}' as store
        FROM products 
        WHERE ${priceCol} > 500
      `;

            const params: any[] = [];
            if (category) {
                query += ` AND category = ?`;
                params.push(category);
            }

            if (search) {
                query += ` AND (${nameCol} LIKE ? OR ${brandCol} LIKE ?)`;
                params.push(`%${search}%`);
                params.push(`%${search}%`);
            }

            query += ` ORDER BY last_seen DESC LIMIT ? OFFSET ?`;
            params.push(limit);
            params.push(offset);

            const rows = db.prepare(query).all(...params) as any[];

            rows.forEach(r => {
                const key = makeMatchKey(r.name);
                if (!marketMap[key]) marketMap[key] = [];
                marketMap[key].push(r);
                allProducts.push(r);
            });

            db.close();
        } catch (e) {
            // Ignorar si la DB no existe o está vacía
        }
    }

    // Enriquecer con info de competencia
    const enriched = allProducts.map(p => {
        const key = makeMatchKey(p.name);
        const peers = marketMap[key] || [];
        const others = peers.filter(o => o.store !== p.store);

        return {
            ...p,
            competitors: others.map(o => ({ store: o.store, price: o.price })),
            market_min: others.length > 0 ? Math.min(...others.map(o => o.price)) : null
        };
    });

    // Ordenar por descuento real para mostrar oportunidades primero
    return enriched.sort((a, b) => (b.discount_pct || 0) - (a.discount_pct || 0));
}
