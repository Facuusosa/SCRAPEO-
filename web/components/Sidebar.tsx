"use client";

import React from "react";
import {
    LayoutDashboard,
    Zap,
    BarChart3,
    History,
    Search,
    Shield,
    Package
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const menuItems = [
    { icon: LayoutDashboard, label: "Tablero", href: "/" },
    { icon: Zap, label: "Radar GlITCH", href: "/glitches" },
    { icon: Search, label: "Mercado Total", href: "/market" },
    { icon: BarChart3, label: "Estadísticas", href: "/analytics" },
    { icon: History, label: "Historial", href: "/history" },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="fixed left-0 top-0 h-screen w-64 bg-white border-r border-slate-200 z-50 flex flex-col pt-6">
            {/* Logo */}
            <div className="px-6 mb-10 flex items-center gap-3">
                <div className="w-10 h-10 bg-slate-900 rounded-xl flex items-center justify-center text-white shadow-lg shadow-slate-200 uppercase font-black italic">
                    <Shield size={22} />
                </div>
                <div>
                    <h1 className="text-lg font-black tracking-tighter text-slate-900 leading-none">ODISEO</h1>
                    <span className="text-[10px] uppercase tracking-widest font-bold text-slate-400">Inteligencia</span>
                </div>
            </div>

            {/* Navegación Principal */}
            <nav className="flex-1 px-4 space-y-1">
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest px-4 mb-4">Menú Principal</p>
                {menuItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.label}
                            href={item.href}
                            className={cn(
                                "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group",
                                isActive
                                    ? "bg-slate-900 text-white shadow-md shadow-slate-200"
                                    : "text-slate-500 hover:bg-slate-50 hover:text-slate-900"
                            )}
                        >
                            <item.icon size={20} className={cn(isActive ? "text-white" : "text-slate-400 group-hover:text-slate-600")} />
                            <span className="text-sm font-semibold">{item.label}</span>
                        </Link>
                    );
                })}
            </nav>

            {/* Status del Sistema */}
            <div className="p-6">
                <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100">
                    <div className="flex items-center gap-2 mb-3">
                        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                        <span className="text-[10px] font-bold text-slate-500 uppercase">Sistema Activo</span>
                    </div>
                    <div className="space-y-2">
                        <div className="flex justify-between text-[11px]">
                            <span className="text-slate-500">Bases de Datos</span>
                            <span className="font-bold text-slate-900">6/6 Online</span>
                        </div>
                        <div className="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
                            <div className="w-full h-full bg-emerald-500 rounded-full" />
                        </div>
                    </div>
                </div>
            </div>
        </aside>
    );
}
