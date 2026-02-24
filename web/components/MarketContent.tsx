"use client";

import React, { useState, useMemo, useEffect } from "react";
import { Package, Search, SlidersHorizontal, ArrowUpDown, Filter, X } from "lucide-react";
import { ProductCard } from "@/components/ProductCard";
import { cn } from "@/lib/utils";

interface MarketContentProps {
    initialProducts: any[];
}

export function MarketContent({ initialProducts }: MarketContentProps) {
    const [products, setProducts] = useState(initialProducts);
    const [search, setSearch] = useState("");
    const [category, setCategory] = useState("all");
    const [minGap, setMinGap] = useState(0);
    const [maxPrice, setMaxPrice] = useState(20000000); // 20M por defecto
    const [sort, setSort] = useState("opportunity");

    // SSE Integration (Priority 4: Optimistic UI)
    useEffect(() => {
        const eventSource = new EventSource("/api/events");
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'update' && data.product) {
                // Agregar al principio sin recarga térmica (Optimistic UI)
                setProducts(prev => {
                    const exists = prev.find(p => p.url === data.product.url);
                    if (exists) return prev;
                    return [data.product, ...prev];
                });
            }
        };
        return () => eventSource.close();
    }, []);

    const categories = [
        { id: "all", label: "Todos", icon: "💎" },
        { id: "celular", label: "Celulares", icon: "📱" },
        { id: "tv", label: "TV & Video", icon: "📺" },
        { id: "clima", label: "Clima", icon: "❄️" },
        { id: "notebook", label: "Notebooks", icon: "💻" },
        { id: "electro", label: "Electro", icon: "🍳" }
    ];

    // Lógica de Filtrado Reactivo (Priority 3)
    const filteredProducts = useMemo(() => {
        return products
            .filter(p => {
                const matchesSearch = !search ||
                    p.name.toLowerCase().includes(search.toLowerCase()) ||
                    p.brand?.toLowerCase().includes(search.toLowerCase());

                const matchesCat = category === "all" ||
                    (p.category && p.category.toLowerCase().includes(category)) ||
                    (p.name && p.name.toLowerCase().includes(category));

                const matchesGap = (p.gap_market || 0) >= minGap;
                const matchesPrice = p.price <= maxPrice;

                return matchesSearch && matchesCat && matchesGap && matchesPrice;
            })
            .sort((a, b) => {
                if (sort === "opportunity") return (b.gap_market || 0) - (a.gap_market || 0);
                if (sort === "price_asc") return a.price - b.price;
                return 0;
            });
    }, [products, search, category, minGap, maxPrice, sort]);

    return (
        <div className="flex flex-col min-h-screen">
            {/* Toolbar Superior */}
            <div className="sticky top-0 z-30 bg-white/80 backdrop-blur-xl border-b border-slate-200 px-10 py-6">
                <div className="flex flex-col lg:flex-row gap-6">
                    <div className="relative flex-1 group">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-600 transition-colors" size={20} />
                        <input
                            type="text"
                            placeholder="Buscar en el catálogo unificado..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="w-full bg-slate-50 border border-slate-200 py-3.5 pl-12 pr-6 rounded-2xl text-sm font-bold outline-none focus:ring-4 focus:ring-blue-500/5 focus:border-blue-500 transition-all font-medium"
                        />
                    </div>

                    <div className="flex items-center gap-3">
                        <select
                            value={sort}
                            onChange={(e) => setSort(e.target.value)}
                            className="bg-white border border-slate-200 px-4 py-3 rounded-2xl text-xs font-black uppercase tracking-widest outline-none focus:border-slate-900 transition-all"
                        >
                            <option value="opportunity">Mayor Oportunidad</option>
                            <option value="price_asc">Más Barato</option>
                        </select>
                    </div>
                </div>

                {/* Filtros de Negocio Rápidos */}
                <div className="flex flex-wrap items-center gap-2 mt-6">
                    {categories.map(c => (
                        <button
                            key={c.id}
                            onClick={() => setCategory(c.id)}
                            className={cn(
                                "px-5 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center gap-2",
                                category === c.id ? "bg-slate-900 text-white shadow-lg" : "bg-white border border-slate-200 text-slate-500 hover:border-slate-900"
                            )}
                        >
                            <span>{c.icon}</span>
                            {c.label}
                        </button>
                    ))}

                    <div className="h-6 w-px bg-slate-200 mx-2" />

                    {[10, 20, 30].map(gap => (
                        <button
                            key={gap}
                            onClick={() => setMinGap(minGap === gap ? 0 : gap)}
                            className={cn(
                                "px-5 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all",
                                minGap === gap ? "bg-emerald-600 text-white" : "bg-emerald-50 text-emerald-600 border border-emerald-100"
                            )}
                        >
                            +{gap}% Margen
                        </button>
                    ))}
                </div>
            </div>

            {/* Grid de Productos */}
            <div className="p-10 flex-1">
                <div className="flex items-center justify-between mb-10">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">
                        Mostrando <span className="text-slate-900">{filteredProducts.length}</span> resultados de reventa
                    </p>
                </div>

                {filteredProducts.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
                        {filteredProducts.map((p, i) => (
                            <ProductCard key={i} product={p} />
                        ))}
                    </div>
                ) : (
                    <div className="py-32 flex flex-col items-center justify-center bg-white rounded-[40px] border border-dashed border-slate-200">
                        <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center text-slate-200 mb-6">
                            <Search size={32} />
                        </div>
                        <p className="text-slate-400 font-black uppercase tracking-widest">Sin resultados</p>
                        <button onClick={() => { setSearch(""); setCategory("all"); setMinGap(0); }} className="mt-4 text-blue-600 text-[10px] font-black uppercase tracking-widest underline underline-offset-4">Limpiar Filtros</button>
                    </div>
                )}
            </div>
        </div>
    );
}
