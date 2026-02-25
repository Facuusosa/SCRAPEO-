"use client";

import React, { useState, useMemo, useEffect } from "react";
import {
    Search,
    ChevronDown,
    ChevronRight,
    Filter,
    DollarSign,
    X,
    LayoutGrid,
    PanelLeftClose,
    PanelLeftOpen,
    Menu,
    AlertCircle,
    Store,
    Tag
} from "lucide-react";
import { ProductCard } from "@/components/ProductCard";
import { cn } from "@/lib/utils";

interface MarketContentProps {
    initialProducts: any[] | undefined;
    allCategories: string[] | undefined;
}

export function MarketContent({ initialProducts = [], allCategories = [] }: MarketContentProps) {
    const [products, setProducts] = useState(initialProducts);
    const [search, setSearch] = useState("");
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
    const [selectedStores, setSelectedStores] = useState<string[]>([]);
    const [minProfit, setMinProfit] = useState<number>(0);
    const [minPrice, setMinPrice] = useState<number>(0);
    const [maxPrice, setMaxPrice] = useState<number>(20000000);
    const [sort, setSort] = useState("opportunity");

    // UI State
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    // Grouping categories (Master List) - REPARADO PARA COMPACIDAD
    const mainCategories = useMemo(() => {
        if (!allCategories || !Array.isArray(allCategories)) return [];
        const uniqueMains = new Set<string>();
        allCategories.forEach(cat => {
            if (!cat || typeof cat !== 'string') return;
            const main = cat.split('/')[0].replace(/-/g, ' ').toUpperCase();
            if (main) uniqueMains.add(main);
        });
        return Array.from(uniqueMains).sort();
    }, [allCategories]);

    const activeStores = useMemo(() => {
        const stores = new Set<string>();
        if (products && Array.isArray(products)) {
            products.forEach(p => { if (p?.store) stores.add(p.store); });
        }
        return Array.from(stores).sort();
    }, [products]);

    // Robust Filtering
    const filteredProducts = useMemo(() => {
        if (!products || !Array.isArray(products)) return [];

        return products
            .filter(p => {
                if (!p) return false;
                const searchLower = search.toLowerCase();
                const matchesSearch = !search ||
                    (p.name?.toLowerCase().includes(searchLower)) ||
                    (p.brand?.toLowerCase().includes(searchLower)) ||
                    (p.category?.toLowerCase().includes(searchLower));
                if (!matchesSearch) return false;

                const matchesCat = !selectedCategory ||
                    (p.category && p.category.toLowerCase().includes(selectedCategory.toLowerCase().replace(/ /g, '-')));
                if (!matchesCat) return false;

                const matchesStore = selectedStores.length === 0 || selectedStores.includes(p.store);
                if (!matchesStore) return false;

                const profitArs = (p.market_min && p.market_min > p.price) ? (p.market_min - p.price) : -1;
                const matchesProfit = minProfit <= 0 || (profitArs >= minProfit);
                if (!matchesProfit) return false;

                const price = p.price || 0;
                const matchesPrice = price >= minPrice && (maxPrice <= 0 || price <= maxPrice);
                if (!matchesPrice) return false;

                return true;
            })
            .sort((a, b) => {
                if (sort === "opportunity") return (b.gap_market || 0) - (a.gap_market || 0);
                if (sort === "price_asc") return a.price - b.price;
                return 0;
            });
    }, [products, search, selectedCategory, selectedStores, minProfit, minPrice, maxPrice, sort]);

    useEffect(() => {
        const eventSource = new EventSource("/api/events");
        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'update' && data.product) {
                    setProducts(prev => {
                        if (prev.find(p => p.url === data.product.url)) return prev;
                        return [data.product, ...prev];
                    });
                }
            } catch (e) { console.error("Real-time error:", e); }
        };
        return () => eventSource.close();
    }, []);

    const SidebarContent = () => (
        <div className="flex flex-col h-full bg-white">
            {/* Header Filtros Compacto */}
            <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-white sticky top-0 z-10">
                <div className="flex items-center gap-2">
                    <Filter size={16} className="text-blue-600" />
                    <span className="text-[10px] font-black uppercase tracking-widest text-slate-900 font-geist">Filtros Activos</span>
                </div>
                <button onClick={() => setIsSidebarOpen(false)} className="hidden lg:block text-slate-400 hover:text-slate-900 transition-colors">
                    <PanelLeftClose size={18} />
                </button>
            </div>

            <div className="flex-1 overflow-y-auto p-5 space-y-6 scrollbar-hide">
                {/* Search Compacto */}
                <div className="relative group">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-600 transition-colors" size={12} />
                    <input
                        type="text"
                        placeholder="Buscar producto..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full bg-slate-50 border border-slate-200 py-2.5 pl-9 pr-4 rounded-xl text-[11px] font-bold outline-none focus:ring-4 focus:ring-blue-500/5 focus:border-blue-500 transition-all font-geist"
                    />
                </div>

                {/* Categorías en FILA (Lista Compacta) */}
                <div className="space-y-3">
                    <label className="text-[9px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
                        <Tag size={10} /> Categorías del Mercado
                    </label>
                    <div className="flex flex-col gap-1">
                        <button
                            onClick={() => setSelectedCategory(null)}
                            className={cn(
                                "w-full text-left px-3 py-2 rounded-lg text-[10px] font-black uppercase tracking-wider transition-all",
                                !selectedCategory ? "bg-slate-900 text-white shadow-lg" : "text-slate-500 hover:bg-slate-100"
                            )}
                        >
                            Ver Todo
                        </button>
                        <div className="border-t border-slate-50 my-1" />
                        <div className="space-y-[2px]"> {/* Espaciado Mínimo */}
                            {mainCategories.map(cat => (
                                <button
                                    key={cat}
                                    onClick={() => setSelectedCategory(cat)}
                                    className={cn(
                                        "w-full text-left px-3 py-1.5 rounded-md text-[10px] font-bold transition-all flex items-center justify-between group",
                                        selectedCategory === cat ? "bg-blue-600 text-white" : "text-slate-600 hover:bg-slate-50"
                                    )}
                                >
                                    <span className="truncate pr-2">{cat}</span>
                                    {selectedCategory === cat && <ChevronRight size={10} className="text-white" />}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Tiendas Compactas */}
                <div className="space-y-3">
                    <label className="text-[9px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
                        <Store size={10} /> Retailers
                    </label>
                    <div className="grid grid-cols-1 gap-1">
                        {activeStores.map(store => (
                            <button
                                key={store}
                                onClick={() => {
                                    setSelectedStores(prev =>
                                        prev.includes(store) ? prev.filter(s => s !== store) : [...prev, store]
                                    );
                                }}
                                className={cn(
                                    "flex items-center gap-3 px-3 py-2 rounded-lg text-[10px] font-bold transition-all text-left",
                                    selectedStores.includes(store)
                                        ? "bg-slate-900 text-white"
                                        : "bg-white border border-slate-200 text-slate-500 hover:border-slate-400 hover:text-slate-900"
                                )}
                            >
                                <span className={cn("w-1.5 h-1.5 rounded-full", selectedStores.includes(store) ? "bg-blue-400" : "bg-slate-200")} />
                                {store}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Margen */}
                <div className="pt-4 border-t border-slate-100 space-y-3">
                    <label className="text-[9px] font-black text-emerald-600 uppercase tracking-widest flex items-center gap-2">
                        <DollarSign size={10} /> Margen Mínimo (ARS)
                    </label>
                    <div className="relative">
                        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-emerald-600 font-bold text-xs">$</span>
                        <input
                            type="number"
                            value={minProfit || ""}
                            onChange={(e) => setMinProfit(Number(e.target.value))}
                            placeholder="0"
                            className="w-full bg-emerald-50/30 border border-emerald-100 py-2.5 pl-7 pr-4 rounded-xl text-[11px] font-black text-emerald-700 outline-none focus:border-emerald-500 transition-all"
                        />
                    </div>
                </div>
            </div>
        </div>
    );

    return (
        <div className="flex w-full h-[calc(100vh-140px)] overflow-hidden bg-white">
            {/* Sidebar Desktop Compacto */}
            {isSidebarOpen ? (
                <aside className="hidden lg:block w-64 flex-shrink-0 h-full border-r border-slate-100 z-10 transition-all duration-300">
                    <SidebarContent />
                </aside>
            ) : null}

            {/* Mobile Menu */}
            {isMobileMenuOpen && (
                <div className="fixed inset-0 z-[100] bg-slate-900/60 lg:hidden" onClick={() => setIsMobileMenuOpen(false)}>
                    <div className="absolute left-0 top-0 bottom-0 w-64 bg-white" onClick={e => e.stopPropagation()}>
                        <SidebarContent />
                    </div>
                </div>
            )}

            {/* Main Area */}
            <main className="flex-1 flex flex-col h-full bg-slate-50/30 min-w-0 transition-all duration-300">
                {/* Internal Toolbar Compacto */}
                <div className="bg-white px-8 py-4 border-b border-slate-100 flex items-center justify-between shadow-sm z-20">
                    <div className="flex items-center gap-4">
                        {!isSidebarOpen && (
                            <button
                                onClick={() => setIsSidebarOpen(true)}
                                className="hidden lg:flex p-2 bg-slate-900 text-white rounded-lg hover:scale-105 active:scale-95 transition-all"
                            >
                                <PanelLeftOpen size={16} />
                            </button>
                        )}
                        <button
                            onClick={() => setIsMobileMenuOpen(true)}
                            className="lg:hidden p-2 bg-slate-100 text-slate-600 rounded-lg"
                        >
                            <Menu size={16} />
                        </button>
                        <div className="flex items-center gap-3">
                            <div className="h-4 w-1 bg-blue-600 rounded-full" />
                            <span className="text-[10px] font-black text-slate-900 uppercase tracking-widest uppercase">
                                {filteredProducts.length} Activos
                            </span>
                        </div>
                    </div>

                    <select
                        value={sort}
                        onChange={(e) => setSort(e.target.value)}
                        className="bg-slate-50 border border-slate-200 px-3 py-2 rounded-lg text-[9px] font-black uppercase tracking-widest outline-none cursor-pointer hover:border-slate-900 transition-all"
                    >
                        <option value="opportunity">ORDENAR POR MARGEN</option>
                        <option value="price_asc">ORDENAR POR PRECIO</option>
                    </select>
                </div>

                {/* Content Grid */}
                <div className="flex-1 overflow-y-auto p-8 scrollbar-hide">
                    {filteredProducts.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-6 pb-20">
                            {filteredProducts.map((p, i) => (
                                <div key={i} className="h-[520px]">
                                    <ProductCard product={p} />
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center bg-white rounded-[32px] border border-dashed border-slate-200 m-4">
                            <AlertCircle size={32} className="text-slate-200 mb-4" />
                            <h3 className="text-[11px] font-black text-slate-900 uppercase tracking-widest">Sin resultados</h3>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}
