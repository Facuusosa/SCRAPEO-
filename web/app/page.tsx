import { getUnifiedProducts } from "@/lib/db";
import { ProductCard } from "@/components/ProductCard";
import { Search, Filter, TrendingUp, X } from "lucide-react";
import Link from "next/link";

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const params = await searchParams;
  const search = typeof params.search === 'string' ? params.search : "";
  const category = typeof params.category === 'string' ? params.category : null;

  const products = getUnifiedProducts(category as any, search);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header Minimalista */}
      <header className="mb-12">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <Link href="/" className="inline-block">
              <h1 className="text-3xl font-black text-slate-900 tracking-tight mb-2">
                Odiseo <span className="text-blue-600">Monitor</span>
              </h1>
            </Link>
            <p className="text-slate-500 font-medium">
              Panel Inteligente de Precios y Arbitraje
            </p>
          </div>

          <div className="flex items-center gap-4">
            <div className="bg-green-100 text-green-700 px-4 py-2 rounded-full text-xs font-bold flex items-center gap-2">
              <TrendingUp size={14} /> {products.length.toLocaleString()} Productos
            </div>
            <div className="hidden sm:block bg-slate-100 text-slate-600 px-4 py-2 rounded-full text-xs font-bold">
              Actualizado hoy
            </div>
          </div>
        </div>

        {/* Buscador y Filtros Sencillos */}
        <div className="mt-10">
          <form action="/" method="GET" className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative md:col-span-3">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
              <input
                type="text"
                name="search"
                defaultValue={search}
                placeholder="Buscar por modelo, marca o producto..."
                className="w-full pl-12 pr-4 py-3 bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
              {search && (
                <Link href="/" className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                  <X size={18} />
                </Link>
              )}
            </div>
            <button type="submit" className="bg-blue-600 text-white rounded-xl py-3 text-sm font-bold hover:bg-blue-700 transition-all shadow-lg shadow-blue-500/20">
              Buscar Ahora
            </button>
          </form>

          {/* Categorías Rápidas */}
          <div className="flex flex-wrap gap-2 mt-4">
            {['Celulares', 'Notebooks', 'TV', 'Aires'].map((cat) => (
              <Link
                key={cat}
                href={`/?category=${cat.toLowerCase()}`}
                className={`px-4 py-1.5 rounded-full text-xs font-bold border transition-all ${category === cat.toLowerCase()
                    ? 'bg-blue-600 border-blue-600 text-white'
                    : 'bg-white border-slate-200 text-slate-600 hover:border-blue-400'
                  }`}
              >
                {cat}
              </Link>
            ))}
          </div>
        </div>
      </header>

      {/* Grid de Productos Real */}
      <main>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-slate-800">
            {search ? `Resultados para "${search}"` : category ? `Categoría: ${category}` : 'Mejores Oportunidades'}
          </h2>
          <span className="text-sm text-slate-500">Ordenado por % de Descuento</span>
        </div>

        {products.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-2xl p-20 text-center">
            <div className="text-slate-300 mb-4 flex justify-center">
              <Search size={48} />
            </div>
            <h3 className="text-xl font-bold text-slate-800 mb-2">No se encontraron productos</h3>
            <p className="text-slate-500">Prueba con otros términos o asegúrate de que los scrapers estén activos.</p>
            {(search || category) && (
              <Link href="/" className="mt-6 inline-block text-blue-600 font-bold hover:underline">
                Limpiar filtros
              </Link>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {products.map((p, idx) => (
              <ProductCard key={idx} product={p as any} />
            ))}
          </div>
        )}
      </main>

      <footer className="mt-20 py-10 border-t border-slate-200 text-center text-slate-400 text-xs font-medium uppercase tracking-widest">
        Sistema Odiseo v5.6 - Inteligencia de Mercado en Tiempo Real
      </footer>
    </div>
  );
}
