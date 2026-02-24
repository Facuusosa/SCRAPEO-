
import { getUnifiedProducts } from "@/lib/db";
import { ProductCard } from "@/components/ProductCard";
import { Package, Search, SlidersHorizontal } from "lucide-react";

interface PageProps {
    searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export default async function MarketPage({ searchParams }: PageProps) {
    const params = await searchParams;
    const query = typeof params.q === 'string' ? params.q : "";

    // Traemos un lote grande por defecto en el mercado total
    const products = await getUnifiedProducts(null, query, 1000);

    return (
        <main className="min-h-screen pl-64 bg-slate-50">
            <div className="bg-white border-b border-slate-200 px-10 py-12">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center text-white shadow-xl shadow-blue-100">
                            <Package size={24} />
                        </div>
                        <div>
                            <h1 className="text-3xl font-black text-slate-900 tracking-tight uppercase">Mercado Total</h1>
                            <p className="text-slate-500 font-medium tracking-tight">Explora el catálogo unificado de todas las tiendas monitoreadas.</p>
                        </div>
                    </div>

                    <form action="/market" className="relative w-full md:w-96 group">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-600 transition-colors" size={18} />
                        <input
                            type="text"
                            name="q"
                            defaultValue={query}
                            placeholder="Buscar producto, marca o SKU..."
                            className="w-full bg-slate-50 border border-slate-200 py-3 pl-12 pr-4 rounded-2xl text-sm font-medium outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 transition-all"
                        />
                    </form>
                </div>

                <div className="flex items-center gap-3 mt-8 overflow-x-auto pb-2 scrollbar-hide">
                    <button className="bg-slate-900 text-white px-5 py-2 rounded-xl text-xs font-bold uppercase tracking-widest flex items-center gap-2">
                        <SlidersHorizontal size={14} />
                        Filtros
                    </button>
                    {["Tecnología", "Audio", "Electro", "Hogar"].map(cat => (
                        <button key={cat} className="bg-white border border-slate-200 text-slate-600 px-5 py-2 rounded-xl text-xs font-bold uppercase tracking-widest hover:border-slate-900 hover:text-slate-900 transition-all">
                            {cat}
                        </button>
                    ))}
                </div>
            </div>

            <div className="p-10">
                <div className="flex items-center justify-between mb-8">
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-[0.2em]">
                        Mostrando <span className="text-slate-900">{products.length}</span> resultados
                    </p>
                </div>

                {products.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
                        {products.map((p, i) => (
                            <ProductCard key={i} product={p} />
                        ))}
                    </div>
                ) : (
                    <div className="py-20 text-center">
                        <p className="text-slate-400 font-bold uppercase tracking-widest">No se encontraron productos para "{query}"</p>
                    </div>
                )}
            </div>
        </main>
    );
}
