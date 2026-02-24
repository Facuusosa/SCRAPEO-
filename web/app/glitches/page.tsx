
import { getUnifiedProducts } from "@/lib/db";
import { ProductCard } from "@/components/ProductCard";
import { Zap, Filter, Search } from "lucide-react";

export default async function GlitchesPage() {
    const products = await getUnifiedProducts(null, "", 500, 0, true);

    return (
        <main className="min-h-screen pl-64 bg-slate-50">
            <div className="bg-white border-b border-slate-200 px-10 py-12">
                <div className="flex items-center gap-4 mb-4">
                    <div className="w-12 h-12 bg-red-600 rounded-2xl flex items-center justify-center text-white shadow-xl shadow-red-100">
                        <Zap size={24} fill="white" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-black text-slate-900 tracking-tight uppercase">Radar de Glitches</h1>
                        <p className="text-slate-500 font-medium">Oportunidades de oro detectadas por anomalía de precio o gap de mercado masivo.</p>
                    </div>
                </div>
            </div>

            <div className="p-10">
                {products.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
                        {products.map((p, i) => (
                            <ProductCard key={i} product={p} />
                        ))}
                    </div>
                ) : (
                    <div className="flex flex-col items-center justify-center py-32 text-center">
                        <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center text-slate-300 mb-6">
                            <Search size={40} />
                        </div>
                        <h2 className="text-xl font-bold text-slate-900">Buscando Glitches...</h2>
                        <p className="text-slate-500 max-w-xs mt-2">
                            El bot está recorriendo las tiendas. Las alertas aparecerán aquí en cuanto se detecten.
                        </p>
                    </div>
                )}
            </div>
        </main>
    );
}
