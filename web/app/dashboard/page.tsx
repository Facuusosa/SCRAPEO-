import { auth } from "@/auth";
import { redirect } from "next/navigation";
import { RadarExplore } from "@/components/RadarExplore";

export default async function DashboardPage() {
    const session = await auth();

    /*
    if (!session) {
        redirect("/login");
    }

    const userTier = (session.user as any).tier || "free";
    const isVip = (session.user as any).isVip || false;

    if (!isVip && userTier === "free") {
        redirect("/#pricing");
    }
    */
    const userTier = "pro"; // Bypass para auditoría
    const isVip = true;

    return (
        <div className="min-h-screen bg-[#030305] text-white p-8 lg:pl-64">
            <div className="max-w-7xl mx-auto pt-8">
                <header className="flex justify-between items-end mb-16">
                    <div>
                        <div className="flex items-center gap-2 mb-2">
                            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                            <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Radar Pro Activo</span>
                        </div>
                        <h1 className="text-5xl font-black tracking-tighter">DASHBOARD <span className="text-emerald-500">PRO</span></h1>
                        <p className="text-slate-400 mt-2 font-medium">Bienvenido, {session.user?.email} | Explorando el mercado en tiempo real.</p>
                    </div>
                </header>

                <RadarExplore userTier={userTier} />
            </div>
        </div>
    );
}
