
import { getUnifiedProducts } from "@/lib/db";
import { MarketContent } from "@/components/MarketContent";
import { Package } from "lucide-react";
import fs from "fs";
import path from "path";

export default async function MarketPage() {
    // Priority 2: 'Mercado Total' debe traer todos los productos (limit 10000 para explorador completo)
    // El filtrado posterior se hace en el cliente para respuesta instantánea (Priority 3)
    const products = await getUnifiedProducts(null, "", 10000);

    // CRÍTICO 1: Cargar categorías maestras para evitar catálogo oculto
    let allCategories: string[] = [];
    try {
        const catPath = path.resolve(process.cwd(), "..", "data", "clean_categories.json");
        if (fs.existsSync(catPath)) {
            allCategories = JSON.parse(fs.readFileSync(catPath, 'utf-8'));
        }
    } catch (e) {
        console.error("Error cargando categorías maestras:", e);
    }

    return (
        <main className="min-h-screen lg:pl-64 bg-slate-50 flex flex-col">
            {/* Header Fijo */}
            <div className="bg-white px-10 pt-12 pb-6 border-b border-slate-100">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center text-white shadow-xl shadow-blue-100">
                        <Package size={24} />
                    </div>
                    <div>
                        <h1 className="text-3xl font-black text-slate-900 tracking-tight uppercase leading-none mb-1">Mercado Pro</h1>
                        <p className="text-slate-500 font-medium text-[10px] uppercase tracking-widest">Explorador de Arbitraje Unificado</p>
                    </div>
                </div>
            </div>

            {/* Contenido Reactivo (Fase 3 y 4) */}
            <MarketContent initialProducts={products} allCategories={allCategories} />
        </main>
    );
}
