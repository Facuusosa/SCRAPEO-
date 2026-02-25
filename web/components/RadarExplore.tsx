"use client";

import React, { useState, useEffect } from "react";
import { Loader2, TrendingDown, Store, DollarSign, ExternalLink } from "lucide-react";
import { cn } from "@/lib/utils";

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
            <div className="flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-emerald-500/10 rounded-2xl flex items-center justify-center text-emerald-500">
                        <TrendingDown size={24} />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold">Radar de Ganancia Híbrido</h2>
                        <p className="text-sm text-slate-400">Mostrando {items.length} de {total} oportunidades detectadas</p>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {items.map((item, idx) => {
                    const profit = item.market_min ? item.market_min - item.price : 0;
                    return (
                        <div key={`${item.name}-${idx}`} className="group bg-white/5 border border-white/10 rounded-[24px] overflow-hidden hover:border-emerald-500/30 transition-all flex flex-col">
                            <div className="aspect-square bg-white p-6 relative flex items-center justify-center">
                                <img src={item.img} alt={item.name} className="max-h-full max-w-full object-contain" />
                                <div className="absolute top-4 left-4">
                                    <div className="bg-slate-900 text-white px-3 py-1 rounded-full text-[10px] font-black uppercase flex items-center gap-2">
                                        <Store size={10} /> {item.store}
                                    </div>
                                </div>
                                {item.gap_market > 0 && (
                                    <div className="absolute top-4 right-4">
                                        <div className="bg-emerald-500 text-white px-3 py-1 rounded-full text-[10px] font-black uppercase shadow-lg">
                                            GAP {item.gap_market.toFixed(0)}%
                                        </div>
                                    </div>
                                )}
                            </div>
                            <div className="p-6 flex-1 flex flex-col">
                                <div className="flex justify-between items-start mb-2">
                                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{item.brand}</span>
                                    {item.discount_pct > 0 && <span className="text-[10px] font-bold text-emerald-500">-{item.discount_pct}% OFF</span>}
                                </div>
                                <h3 className="font-bold text-slate-200 line-clamp-2 mb-4 group-hover:text-white transition-colors">{item.name}</h3>

                                <div className="mt-auto space-y-4">
                                    <div className="bg-white/5 rounded-xl p-3 flex justify-between items-center border border-white/5">
                                        <div className="text-xs text-slate-500 uppercase font-bold tracking-wider">Precio</div>
                                        <div className="text-lg font-black text-white">{formatPrice(item.price)}</div>
                                    </div>

                                    {profit > 0 && (
                                        <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs px-1">
                                            <DollarSign size={14} />
                                            <span>Ganancia est. {formatPrice(profit)}</span>
                                        </div>
                                    )}

                                    <a
                                        href={item.url}
                                        target="_blank"
                                        className="w-full py-3 bg-white/10 hover:bg-emerald-500 hover:text-black rounded-xl text-center text-xs font-bold transition-all flex items-center justify-center gap-2"
                                    >
                                        VER EN TIENDA <ExternalLink size={14} />
                                    </a>
                                </div>
                            </div>
                        </div>
                    );
                })}
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
