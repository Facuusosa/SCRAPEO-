"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface PriceChartProps {
    currentPrice: number;
    competitors?: { store: string; price: number }[];
    marketMin?: number | null;
}

export const PriceEvolutionChart = ({ currentPrice, competitors = [], marketMin }: PriceChartProps) => {
    const formatPrice = (p: number) => {
        return new Intl.NumberFormat("es-AR", {
            style: "currency",
            currency: "ARS",
            maximumFractionDigits: 0,
        }).format(p || 0);
    };

    const hasCompetitors = competitors && competitors.length > 0;

    return (
        <div className="py-2">
            <div className="flex justify-between items-center mb-3">
                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Comparativa Real</span>
                {marketMin && (
                    <div className="text-[10px] font-bold text-slate-900">
                        Min. Mercado: <span className="text-emerald-600">{formatPrice(marketMin)}</span>
                    </div>
                )}
            </div>

            <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
                {!hasCompetitors ? (
                    <div className="h-[80px] flex flex-col items-center justify-center text-center gap-2">
                        <div className="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
                            <div className="w-1/3 h-full bg-slate-300 animate-pulse" />
                        </div>
                        <span className="text-[9px] font-bold text-slate-400 uppercase tracking-tighter">Buscando datos de la competencia...</span>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {/* Barra Actual */}
                        <div className="space-y-1">
                            <div className="flex justify-between text-[9px] font-black uppercase tracking-tight text-slate-900">
                                <span>Esta Oferta</span>
                                <span>{formatPrice(currentPrice)}</span>
                            </div>
                            <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
                                <div className="h-full bg-slate-900 rounded-full" style={{ width: '100%' }} />
                            </div>
                        </div>

                        {/* Barras Competencia */}
                        {competitors.slice(0, 3).map((comp, i) => {
                            const diff = ((comp.price - currentPrice) / currentPrice) * 100;
                            const barWidth = Math.min(100, (currentPrice / comp.price) * 100);

                            return (
                                <div key={i} className="space-y-1">
                                    <div className="flex justify-between text-[9px] font-bold uppercase tracking-tight text-slate-400">
                                        <span>{comp.store}</span>
                                        <div className="flex gap-2">
                                            <span className="text-slate-600">{formatPrice(comp.price)}</span>
                                            <span className="text-emerald-500">+{diff.toFixed(0)}%</span>
                                        </div>
                                    </div>
                                    <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
                                        <div className="h-full bg-blue-500/30 rounded-full" style={{ width: `${barWidth}%` }} />
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                )}
            </div>

            {marketMin && currentPrice < marketMin && (
                <div className="mt-3 bg-emerald-50 border border-emerald-100 rounded-lg p-2 flex items-center justify-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="text-[10px] font-black text-emerald-700 uppercase tracking-tighter">
                        ¡PRECIO DE ARBITRAJE DETECTADO!
                    </span>
                </div>
            )}
        </div>
    );
};
