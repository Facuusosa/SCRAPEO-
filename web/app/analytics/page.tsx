
import { BarChart3, TrendingUp, Users, ShoppingCart } from "lucide-react";

export default function AnalyticsPage() {
    return (
        <main className="min-h-screen pl-64 bg-slate-50">
            <div className="bg-white border-b border-slate-200 px-10 py-12">
                <div className="flex items-center gap-4 mb-4">
                    <div className="w-12 h-12 bg-purple-600 rounded-2xl flex items-center justify-center text-white shadow-xl shadow-purple-100">
                        <BarChart3 size={24} />
                    </div>
                    <div>
                        <h1 className="text-3xl font-black text-slate-900 tracking-tight uppercase">Estadísticas de Mercado</h1>
                        <p className="text-slate-500 font-medium tracking-tight">Análisis profundo de tendencias, inflación y stock en tiempo real.</p>
                    </div>
                </div>
            </div>

            <div className="p-10 grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="bg-white p-8 rounded-3xl border border-slate-200 pro-shadow">
                    <div className="w-10 h-10 bg-emerald-50 text-emerald-600 rounded-xl flex items-center justify-center mb-6">
                        <TrendingUp size={20} />
                    </div>
                    <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Inflación Diaria</h3>
                    <p className="text-3xl font-black text-slate-900">-2.4%</p>
                    <p className="text-xs text-slate-400 mt-2">Tendencia bajista en electrónica</p>
                </div>
                {/* Repetir para otros stats */}
            </div>

            <div className="p-10 text-center py-20">
                <p className="text-slate-400 font-bold uppercase tracking-[0.2em] animate-pulse">
                    Módulos de inteligencia avanzada en proceso de carga...
                </p>
            </div>
        </main>
    );
}
