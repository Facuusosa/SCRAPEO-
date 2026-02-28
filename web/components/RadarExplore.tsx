"use client";

import React, { useState, useEffect } from "react";
import { Loader2, TrendingDown, Store, DollarSign, ExternalLink, Zap } from "lucide-react";
import { cn } from "@/lib/utils";
import { ProductCard } from "./ProductCard";

interface RadarItem {
    name: string;
    price: number;
    list_price: number;
    discount_pct: number;
    brand: string;
    img: string;
    url: string;
    store: string;
    gap_market: number;
    market_min: number;
}

export function RadarExplore({ userTier }: { userTier: string }) {
    const [items, setItems] = useState<RadarItem[]>([]);
    const [total, setTotal] = useState(0);
    const [offset, setOffset] = useState(0);
    const [loading, setLoading] = useState(false);
    const [hasMore, setHasMore] = useState(true);

    const limit = 20;

    const fetchRadar = async (newOffset: number, append = true) => {
        setLoading(true);
        try {
            const res = await fetch(`/api/radar?limit=${limit}&offset=${newOffset}`);
            const data = await res.json();

            if (data.success) {
                setTotal(data.total);
                if (append) {
                    setItems(prev => [...prev, ...data.items]);
                } else {
                    setItems(data.items);
                }
                setHasMore(data.items.length === limit);
            }
        } catch (error) {
            console.error("Error fetching radar:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRadar(0, false);
    }, []);

    const loadMore = () => {
        const nextOffset = offset + limit;
        setOffset(nextOffset);
        fetchRadar(nextOffset, true);
    };

    const formatPrice = (p: number) => {
        return new Intl.NumberFormat("es-AR", {
            style: "currency",
            currency: "ARS",
            maximumFractionDigits: 0,
        }).format(p);
    };

    return (
        <div className="space-y-8">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 bg-white p-10 rounded-[40px] border border-slate-200 shadow-sm mb-12">
                <div className="flex items-center gap-6">
                    <div className="w-16 h-16 bg-slate-900 rounded-[22px] flex items-center justify-center text-white shadow-xl shadow-slate-200">
                        <TrendingDown size={32} />
                    </div>
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <span className="text-[9px] font-black text-emerald-600 uppercase tracking-[0.3em] bg-emerald-50 px-2 py-0.5 rounded">Live</span>
                            <h2 className="text-3xl font-black text-slate-900 uppercase tracking-tighter">Radar de Ganancia <span className="text-emerald-500 italic">Híbrido</span></h2>
                        </div>
                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
                            Explorando {total.toLocaleString()} oportunidades detectadas por inteligencia artificial
                        </p>
                    </div>
                </div>
                <div className="flex flex-col items-end">
                    <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Frecuencia de escaneo</span>
                    <span className="text-sm font-black text-slate-900">Tiempo Real (2s)</span>
                </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-4">
                {items.length > 0 ? (
                    items.map((item, idx) => (
                        <ProductCard key={`${item.name}-${idx}`} product={item} />
                    ))
                ) : !loading && (
                    <div className="col-span-full py-32 text-center bg-white rounded-[40px] border border-dashed border-slate-200">
                        <div className="flex flex-col items-center gap-4">
                            <div className="w-12 h-12 bg-slate-50 rounded-full flex items-center justify-center animate-spin text-slate-300">
                                <TrendingDown size={20} />
                            </div>
                            <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em]">Sincronizando brechas de rentabilidad...</p>
                        </div>
                    </div>
                )}
            </div>

            {loading && (
                <div className="py-12 flex justify-center">
                    <Loader2 className="animate-spin text-emerald-500" />
                </div>
            )}

            {!loading && hasMore && (
                <div className="py-12 flex justify-center">
                    <button
                        onClick={loadMore}
                        className="px-8 py-4 bg-white/10 hover:bg-white text-white hover:text-black rounded-2xl font-bold text-sm transition-all border border-white/10"
                    >
                        Cargar más oportunidades
                    </button>
                </div>
            )}

            {!hasMore && items.length > 0 && (
                <p className="text-center text-slate-500 text-sm font-medium py-12">Has llegado al final del radar.</p>
            )}
        </div>
    );
}
