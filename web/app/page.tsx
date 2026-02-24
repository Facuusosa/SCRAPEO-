import { LucideIcon, TrendingDown, Zap, BarChart3, ArrowUpRight, ArrowDownRight, ShieldCheck, Search } from "lucide-react";
import { ProductCard } from "@/components/ProductCard";
import { getUnifiedProducts } from "@/lib/db";
import { cn } from "@/lib/utils";

async function getStats() {
  const products = await getUnifiedProducts(null, "", 5000);
  const opportunities = products.filter(p => p.gap_market > 12);
  const avgOpportunity = opportunities.length > 0
    ? opportunities.reduce((acc, p) => acc + (p.gap_market || 0), 0) / opportunities.length
    : 0;

  return {
    totalProducts: products.length,
    glitchesFound: opportunities.length,
    avgOpportunity: avgOpportunity.toFixed(1),
    activeSources: 6
  };
}

export default async function DashboardPage() {
  const products = await getUnifiedProducts(null, "", 1000);
  const stats = await getStats();

  // Radar de Oportunidades: Solo lo que realmente deja margen
  const highlightProducts = products
    .filter(p => p.gap_market > 15)
    .sort((a, b) => (b.gap_market || 0) - (a.gap_market || 0))
    .slice(0, 8);

  return (
    <main className="min-h-screen pl-64 bg-slate-50">
      {/* Header / Top Bar */}
      <div className="bg-white border-b border-slate-200 px-10 py-12">
        <div className="flex justify-between items-end">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
              <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Inteligencia de Arbitraje Activa</span>
            </div>
            <h1 className="text-4xl font-black text-slate-900 tracking-tight">Oportunidades de Negocio</h1>
            <p className="text-slate-500 mt-2 max-w-2xl font-medium">
              Analizando en tiempo real el desvío de precios entre los 6 retailers más grandes de Argentina para detectar brechas de reventa inmediata.
            </p>
          </div>
          <div className="flex gap-3">
            <button className="flex items-center gap-2 bg-slate-900 text-white px-6 py-4 rounded-2xl text-[10px] font-black uppercase tracking-widest hover:bg-slate-800 transition-all shadow-xl shadow-slate-200">
              Exportar Oportunidades
              <ArrowUpRight size={14} />
            </button>
          </div>
        </div>

        {/* Grid de Métricas de Negocio */}
        <div className="grid grid-cols-4 gap-6 mt-12">
          <StatCard
            label="Catálogo Monitoreado"
            value={stats.totalProducts.toLocaleString()}
            icon={Search}
            trend="Artículos"
            trendUp={true}
          />
          <StatCard
            label="Alertas de Arbitraje"
            value={stats.glitchesFound}
            icon={Zap}
            trend="Gaps Activos"
            trendUp={false}
            highlight={true}
          />
          <StatCard
            label="Margen de Reventa Promedio"
            value={`${stats.avgOpportunity}%`}
            icon={TrendingDown}
            trend="Mercado"
            trendUp={true}
          />
          <StatCard
            label="Retailers Conectados"
            value={stats.activeSources}
            icon={ShieldCheck}
            trend="Sincronizados"
            trendUp={true}
          />
        </div>
      </div>

      <div className="p-10 space-y-16">
        {/* Radar de Ganancia Inmediata */}
        <section>
          <div className="flex items-center justify-between mb-10">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-emerald-600 rounded-2xl flex items-center justify-center text-white shadow-xl shadow-emerald-100">
                <TrendingDown size={28} />
              </div>
              <div>
                <h2 className="text-2xl font-black text-slate-900 uppercase tracking-tight leading-none mb-1">Radar de Ganancia</h2>
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Brechas superiores al 15% contra el mercado</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {highlightProducts.length > 0 ? (
              highlightProducts.map((product, i) => (
                <ProductCard key={i} product={product} />
              ))
            ) : (
              <div className="col-span-full py-24 text-center bg-white rounded-3xl border border-dashed border-slate-200">
                <p className="text-slate-400 font-bold uppercase tracking-widest italic">Calculando brechas de rentabilidad en tiempo real...</p>
              </div>
            )}
          </div>
        </section>

        {/* Listado General de Mercado */}
        <section className="pb-24">
          <div className="flex items-center justify-between mb-10 border-t border-slate-200 pt-16">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-slate-900 rounded-2xl flex items-center justify-center text-white shadow-xl shadow-slate-200">
                <BarChart3 size={28} />
              </div>
              <div>
                <h2 className="text-2xl font-black text-slate-900 uppercase tracking-tight leading-none mb-1">Mercado Unificado</h2>
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Últimos precios indexados por el monitor</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {products.slice(0, 20).map((product, i) => (
              <ProductCard key={i} product={product} />
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}

function StatCard({ label, value, icon: Icon, trend, trendUp, highlight = false }: {
  label: string,
  value: string | number,
  icon: LucideIcon,
  trend: string,
  trendUp: boolean,
  highlight?: boolean
}) {
  return (
    <div className={cn(
      "p-8 rounded-3xl border transition-all duration-300 pro-shadow",
      highlight ? "bg-slate-900 border-slate-900 text-white" : "bg-white border-slate-200 text-slate-900"
    )}>
      <div className="flex items-start justify-between mb-6">
        <div className={cn(
          "w-12 h-12 rounded-2xl flex items-center justify-center",
          highlight ? "bg-white/10 text-white" : "bg-slate-50 text-slate-900"
        )}>
          <Icon size={24} />
        </div>
        <div className={cn(
          "flex items-center gap-1 text-[9px] font-black uppercase px-3 py-1.5 rounded-full tracking-widest",
          highlight ? "bg-white/10 text-white" : (trendUp ? "bg-emerald-50 text-emerald-600" : "bg-amber-50 text-amber-600")
        )}>
          {trend}
        </div>
      </div>
      <div className="flex flex-col">
        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 mb-1">
          {label}
        </span>
        <span className="text-3xl font-black tracking-tight">{value}</span>
      </div>
    </div>
  );
}
