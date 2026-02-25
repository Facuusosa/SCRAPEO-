import { auth } from "@/auth";
import { redirect } from "next/navigation";
import Database from "better-sqlite3";
import path from "path";
import MarketDashboard from "@/components/market-dashboard"; // Asumiendo que el componente existe o lo crearemos

export default async function DashboardPage() {
    const session = await auth();

    if (!session) {
        redirect("/login");
    }

    const userTier = (session.user as any).tier || "free";
    const isVip = (session.user as any).isVip || false;

    if (!isVip && userTier === "free") {
        // Si es free, podrías mostrar una versión limitada o redirigir a pricing
        // Para el MVP, redirigimos a pricing si intenta entrar al dashboard VIP
        redirect("/#pricing");
    }

    // Conectar a la DB de oportunidades (la del sniffer)
    const snifferDbPath = path.resolve(process.cwd(), "..", "targets", "fravega", "fravega_monitor_v2.db");
    let opportunities = [];

    try {
        const db = new Database(snifferDbPath);
        opportunities = db.prepare("SELECT * FROM opportunities ORDER BY confirmed_at DESC LIMIT 50").all();
    } catch (e) {
        console.error("No se pudo cargar la DB de oportunidades locales, usando datos de integracion.");
        // Fallback a la local si existe
        const localDbPath = path.resolve(process.cwd(), "odiseo_users.db");
        const localDb = new Database(localDbPath);
        opportunities = localDb.prepare("SELECT * FROM opportunities ORDER BY confirmed_at DESC LIMIT 20").all();
    }

    return (
        <div className="min-h-screen bg-[#030305] text-white p-8">
            <div className="max-w-7xl mx-auto">
                <header className="flex justify-between items-center mb-12">
                    <div>
                        <h1 className="text-4xl font-black tracking-tighter">DASHBOARD <span className="text-emerald-500">PRO</span></h1>
                        <p className="text-slate-400">Bienvenido, {session.user?.email} | Plan: <span className="text-emerald-400 font-bold uppercase">{userTier}</span></p>
                    </div>
                    <div className="flex gap-4">
                        <div className="px-4 py-2 bg-white/5 rounded-xl border border-white/10 text-xs font-bold text-slate-400">
                            SERVER STATUS: <span className="text-emerald-500 ml-2">● LIVE</span>
                        </div>
                    </div>
                </header>

                {/* Aquí iría el componente de la tabla de oportunidades que refinamos en sesiones anteriores */}
                <div className="bg-[#0f0f11] border border-white/10 rounded-[32px] p-8">
                    <div className="flex justify-between items-center mb-8">
                        <h2 className="text-2xl font-bold">Oportunidades en Tiempo Real</h2>
                        <div className="flex gap-2">
                            <span className="px-3 py-1 bg-emerald-500/10 text-emerald-500 rounded-full text-xs font-bold border border-emerald-500/20">
                                {opportunities.length} Detectadas
                            </span>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {opportunities.map((opp: any) => (
                            <div key={opp.id} className="bg-white/5 border border-white/5 p-6 rounded-2xl hover:border-emerald-500/30 transition-all group">
                                <div className="flex justify-between items-start mb-4">
                                    <span className="text-xs font-black text-emerald-500 bg-emerald-500/10 px-2 py-1 rounded">GAP {opp.gap_teorico}%</span>
                                    <span className="text-[10px] text-slate-500">{new Date(opp.confirmed_at).toLocaleTimeString()}</span>
                                </div>
                                <h3 className="font-bold text-slate-200 line-clamp-2 mb-4 group-hover:text-white transition-colors">{opp.name}</h3>
                                <div className="flex justify-between items-end">
                                    <div>
                                        <div className="text-xs text-slate-500 uppercase font-bold tracking-wider">Precio</div>
                                        <div className="text-xl font-black text-white">${Number(opp.price).toLocaleString('es-AR')}</div>
                                    </div>
                                    <a href={opp.url} target="_blank" className="p-3 bg-white/10 rounded-xl hover:bg-emerald-500 hover:text-black transition-all">
                                        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
                                    </a>
                                </div>
                            </div>
                        ))}
                        {opportunities.length === 0 && (
                            <div className="col-span-full py-20 text-center text-slate-500">
                                Esperando nuevas señales del sniffer...
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
