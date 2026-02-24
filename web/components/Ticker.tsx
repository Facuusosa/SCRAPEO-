"use client";

import React from "react";
import { Zap } from "lucide-react";

interface TickerItem {
    id: string;
    text: string;
    store: string;
    discount: number;
}

export function TopTicker() {
    // Mock data for the ticker - in a real app this would come from a real-time source
    const glitches: TickerItem[] = [
        { id: "1", text: "iPhone 15 Pro Max 256GB Platinum", store: "Fravega", discount: 45 },
        { id: "1", text: "Smart TV Samsung 65' QLED 4K", store: "Cetrogar", discount: 38 },
        { id: "1", text: "Notebook ASUS ROG Zephyrus G14", store: "Megatone", discount: 52 },
        { id: "1", text: "Aire Acondicionado BGH Silent Air", store: "Newsan", discount: 41 },
        { id: "1", text: "Heladera Samsung Family Hub 600L", store: "OnCity", discount: 35 },
    ];

    return (
        <div className="h-10 bg-slate-950 border-b border-card-border overflow-hidden flex items-center relative z-50">
            <div className="bg-rose-600 h-full px-4 flex items-center gap-2 z-10 shadow-[4px_0_15px_rgba(225,29,72,0.4)]">
                <Zap size={14} className="fill-white text-white animate-pulse" />
                <span className="text-[10px] font-black uppercase tracking-tighter text-white">Glitch Feed</span>
            </div>

            <div className="flex-1 overflow-hidden">
                <div className="animate-ticker whitespace-nowrap inline-flex items-center gap-12 pl-12">
                    {glitches.map((item, i) => (
                        <div key={i} className="flex items-center gap-3">
                            <span className="text-[11px] font-mono text-slate-400 uppercase tracking-widest">{item.store}</span>
                            <span className="text-[11px] font-bold text-slate-100">{item.text}</span>
                            <span className="text-[11px] font-mono text-rose-500 font-black">-{item.discount}%</span>
                            <div className="w-1.5 h-1.5 rounded-full bg-slate-800" />
                        </div>
                    ))}
                    {/* Duplicate for seamless loop */}
                    {glitches.map((item, i) => (
                        <div key={`dup-${i}`} className="flex items-center gap-3">
                            <span className="text-[11px] font-mono text-slate-400 uppercase tracking-widest">{item.store}</span>
                            <span className="text-[11px] font-bold text-slate-100">{item.text}</span>
                            <span className="text-[11px] font-mono text-rose-500 font-black">-{item.discount}%</span>
                            <div className="w-1.5 h-1.5 rounded-full bg-slate-800" />
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
