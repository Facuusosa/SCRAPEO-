"use client";

import React from "react";
import {
    LayoutDashboard,
    Search,
    Shield,
    Terminal
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const menuItems = [
    { icon: LayoutDashboard, label: "Radar de Ofertas", href: "/" },
    { icon: Search, label: "Explorador de Mercado", href: "/market" },
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

            {/* Navegación Principal - Solo 2 Links */}
            <nav className="flex-1 px-4 space-y-1">
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest px-4 mb-4">Navegación</p>
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

                <div className="pt-10">
                    <button
                        onClick={() => window.dispatchEvent(new CustomEvent('toggle-terminal'))}
                        className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-slate-300 hover:text-slate-500 transition-all font-bold text-[10px] uppercase tracking-widest"
                    >
                        <Terminal size={14} />
                        Acceso Sistema
                    </button>
                </div>
            </nav>

            {/* Status del Sistema */}
            <div className="p-6">
                <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100">
                    <div className="flex items-center gap-2 mb-3">
                        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                        <span className="text-[10px] font-bold text-slate-500 uppercase">Red Online</span>
                    </div>
                </div>
            </div>
        </aside>
    );
}
