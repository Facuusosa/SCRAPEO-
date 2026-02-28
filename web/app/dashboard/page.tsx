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
        <div className="min-h-screen bg-slate-50 text-slate-900 p-8 lg:pl-64">
            <div className="max-w-7xl mx-auto pt-8">
                <header className="flex justify-between items-end mb-16 px-4">
                    <div>
                        <div className="flex items-center gap-2 mb-2">
                            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                            <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Radar Pro Activo</span>
                        </div>
                        <h1 className="text-5xl font-black text-slate-900 tracking-tighter uppercase leading-none">DASHBOARD <span className="text-emerald-500 italic">PRO</span></h1>
                        <p className="text-slate-500 mt-4 font-medium max-w-xl leading-relaxed">
                            {session?.user?.email
                                ? `Bienvenido, administrador (${session.user.email}).`
                                : "Explorando brechas de mercado premium en tiempo real para optimizar tu arbitraje."}
                        </p>
                    </div>
                </header>

                <div className="px-4">
                    <RadarExplore userTier={userTier} />
                </div>
            </div>
        </div>
    );
}
