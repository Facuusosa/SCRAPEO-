import { LucideIcon, TrendingDown, Zap, BarChart3, ArrowUpRight, ArrowDownRight, Filter } from "lucide-react";
import { ProductCard } from "@/components/ProductCard";
import { getUnifiedProducts } from "@/lib/db";
import { cn } from "@/lib/utils";

async function getStats() {
  const products = await getUnifiedProducts();
  const glitches = products.filter(p => (p.z_score && p.z_score < -2.5) || p.discount_pct > 50);
  const avgDiscount = products.reduce((acc, p) => acc + p.discount_pct, 0) / products.length;

  return {
    totalProducts: products.length,
    glitchesFound: glitches.length,
    avgDiscount: avgDiscount.toFixed(1),
    activeSources: 4
  };
}

export default async function DashboardPage() {
  const products = await getUnifiedProducts();
  const stats = await getStats();

  // Separar productos normales de glitches para el radar
  const highlightProducts = products
    .filter(p => (p.z_score && p.z_score < -2.0) || p.discount_pct > 40)
    .sort((a, b) => (a.z_score || 0) - (b.z_score || 0))
    .slice(0, 8);

  return (
    <main className="min-h-screen pl-64 bg-slate-50">
      {/* Header / Top Bar */}
      <div className="bg-white border-b border-slate-200 px-10 py-8">
        <div className="flex justify-between items-end">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Mercado en Tiempo Real</span>
            </div>
            <h1 className="text-3xl font-black text-slate-900 tracking-tight">Oportunidades de Arbitraje</h1>
            <p className="text-slate-500 mt-1 max-w-xl">
              Escaneando automáticamente múltiples fuentes para detectar anomalías de precio y oportunidades de reventa masivas.
            </p>
          </div>
          <div className="flex gap-3">
            <button className="flex items-center gap-2 bg-slate-900 text-white px-5 py-3 rounded-2xl text-xs font-bold uppercase tracking-widest hover:bg-slate-800 transition-all shadow-lg shadow-slate-200">
              Descargar Reporte
              <ArrowUpRight size={14} />
            </button>
          </div>
        </div>

        {/* Grid de Estadísticas */}
        <div className="grid grid-cols-4 gap-6 mt-10">
          <StatCard
            label="Productos Indexados"
            value={stats.totalProducts.toLocaleString()}
            icon={BarChart3}
            trend="+1.2k hoy"
            trendUp={true}
          />
          <StatCard
            label="Glitches Detectados"
            value={stats.glitchesFound}
            icon={Zap}
            trend="Críticos"
            trendUp={false}
            highlight={true}
          />
          <StatCard
            label="Descuento Promedio"
            value={`${stats.avgDiscount}%`}
            icon={TrendingDown}
            trend="Optimizado"
            trendUp={true}
          />
          <StatCard
            label="Nodos de Escaneo"
            value={stats.activeSources}
            icon={Filter}
            trend="Sincronizados"
            trendUp={true}
          />
        </div>
      </div>

      <div className="p-10 space-y-12">
        {/* Sección Radar de Glitches */}
        <section>
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-red-100 rounded-2xl flex items-center justify-center text-red-600 shadow-sm border border-red-50">
                <Zap size={24} />
              </div>
              <div>
                <h2 className="text-xl font-black text-slate-900 uppercase tracking-tight">Radar de Anomalías</h2>
                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Glitches de precio críticos detectados hoy</p>
              </div>
            </div>
            <div className="flex gap-2">
              <select className="bg-white border border-slate-200 rounded-xl px-4 py-2 text-[10px] font-black uppercase tracking-widest text-slate-600 outline-none focus:border-slate-900">
                <option>Todas las Tiendas</option>
                <option>Frávega</option>
                <option>Megatone</option>
                <option>Cetrogar</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {highlightProducts.length > 0 ? (
              highlightProducts.map((product, i) => (
                <ProductCard key={i} product={product} />
              ))
            ) : (
              <div className="col-span-full py-20 text-center animate-pulse">
                <p className="text-slate-400 font-bold uppercase tracking-widest">Escaneando mercado en busca de glitches...</p>
              </div>
            )}
          </div>
        </section>

        {/* Sección Mercado General */}
        <section className="pb-24">
          <div className="flex items-center justify-between mb-8 border-t border-slate-200 pt-12">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-slate-100 rounded-2xl flex items-center justify-center text-slate-900 shadow-sm border border-slate-50">
                <BarChart3 size={24} />
              </div>
              <div>
                <h2 className="text-xl font-black text-slate-900 uppercase tracking-tight">Vista General del Mercado</h2>
                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Últimos productos indexados en el sistema</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {products.slice(0, 16).map((product, i) => (
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
      "p-6 rounded-3xl border transition-all duration-300 pro-shadow",
      highlight ? "bg-slate-900 border-slate-900 text-white" : "bg-white border-slate-200 text-slate-900"
    )}>
      <div className="flex items-start justify-between mb-4">
        <div className={cn(
          "w-10 h-10 rounded-xl flex items-center justify-center",
          highlight ? "bg-white/10 text-white" : "bg-slate-50 text-slate-900"
        )}>
          <Icon size={20} />
        </div>
        <div className={cn(
          "flex items-center gap-1 text-[10px] font-bold px-2 py-1 rounded-full",
          highlight ? "bg-white/10 text-white" : (trendUp ? "bg-emerald-50 text-emerald-600" : "bg-amber-50 text-amber-600")
        )}>
          {trendUp ? <ArrowUpRight size={10} /> : <ArrowDownRight size={10} />}
          {trend}
        </div>
      </div>
      <div className="flex flex-col">
        <span className={cn(
          "text-[10px] font-bold uppercase tracking-widest",
          highlight ? "text-slate-400" : "text-slate-400"
        )}>
          {label}
        </span>
        <span className="text-2xl font-black tracking-tight">{value}</span>
      </div>
    </div>
  );
}
