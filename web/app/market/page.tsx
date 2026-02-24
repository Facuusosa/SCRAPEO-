
import { getUnifiedProducts } from "@/lib/db";
import { MarketContent } from "@/components/MarketContent";
import { Package } from "lucide-react";

export default async function MarketPage() {
    // Priority 2: 'Mercado Total' debe traer todos los productos (limit 1000)
    // El filtrado posterior se hace en el cliente para respuesta instantánea (Priority 3)
    const products = await getUnifiedProducts(null, "", 1000);

    return (
        <main className="min-h-screen pl-64 bg-slate-50">
            {/* Header Fijo */}
            <div className="bg-white px-10 pt-12 pb-6">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center text-white shadow-xl shadow-blue-100">
                        <Package size={24} />
                    </div>
                    <div>
                        <h1 className="text-3xl font-black text-slate-900 tracking-tight uppercase leading-none mb-1">Mercado Pro</h1>
                        <p className="text-slate-500 font-medium text-[10px] uppercase tracking-widest">Panel de Arbitraje Unificado • Tiempo Real</p>
                    </div>
                </div>
            </div>

            {/* Contenido Reactivo (Fase 3 y 4) */}
            <MarketContent initialProducts={products} />
        </main>
    );
}
