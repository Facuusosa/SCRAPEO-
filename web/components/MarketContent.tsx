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
    Tag,
    Flame,
    Zap,
    TrendingUp,
    Bomb
} from "lucide-react";
import { ProductCard, Product } from "@/components/ProductCard";
import { cn } from "@/lib/utils";

interface MarketContentProps {
    initialProducts: Product[] | undefined;
    allCategories: string[] | undefined;
}

export function MarketContent({ initialProducts = [], allCategories = [] }: MarketContentProps) {
    const [products, setProducts] = useState<Product[]>(initialProducts);
    const [search, setSearch] = useState("");
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
    const [selectedStores, setSelectedStores] = useState<string[]>([]);
    const [minProfit, setMinProfit] = useState<number>(0);
    const [minMarginPct, setMinMarginPct] = useState<number>(0);
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
        allCategories.forEach((cat: string) => {
            if (!cat || typeof cat !== 'string') return;
            const main = cat.split('/')[0].replace(/-/g, ' ').toUpperCase();
            if (main) uniqueMains.add(main);
        });
        return Array.from(uniqueMains).sort();
    }, [allCategories]);

    const activeStores = useMemo(() => {
        const stores = new Set<string>();
        if (products && Array.isArray(products)) {
            products.forEach((p: Product) => { if (p?.store) stores.add(p.store); });
        }
        return Array.from(stores).sort();
    }, [products]);

    const activeBrands = useMemo(() => {
        const brands = new Set<string>();
        if (products && Array.isArray(products)) {
            products.forEach((p: Product) => { if (p?.brand) brands.add(p.brand); });
        }
        return Array.from(brands).sort().slice(0, 30); // Limite para no saturar
    }, [products]);

    const [selectedBrands, setSelectedBrands] = useState<string[]>([]);

    // Robust Filtering
    const filteredProducts = useMemo(() => {
        if (!products || !Array.isArray(products)) return [];

        return products
            .filter((p: Product) => {
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

                const matchesBrand = selectedBrands.length === 0 || selectedBrands.includes(p.brand);
                if (!matchesBrand) return false;

                const profitArs = (p.market_min && p.market_min > p.price) ? (p.market_min - p.price) : -1;
                const matchesProfit = minProfit <= 0 || (profitArs >= minProfit);
                if (!matchesProfit) return false;

                const marginPct = p.gap_market || 0;
                const matchesMargin = minMarginPct <= 0 || (marginPct >= minMarginPct);
                if (!matchesMargin) return false;

                const price = p.price || 0;
                const matchesPrice = price >= minPrice && (maxPrice <= 0 || price <= maxPrice);
                if (!matchesPrice) return false;

                return true;
            })
            .sort((a: Product, b: Product) => {
                if (sort === "opportunity") return (b.gap_market || 0) - (a.gap_market || 0);
                if (sort === "price_asc") return a.price - b.price;
                return 0;
            });
    }, [products, search, selectedCategory, selectedStores, minProfit, minMarginPct, minPrice, maxPrice, sort]);

    // ZONA DE BOMBAS (Top 4 por mayor porcentaje de Gap)
    const bombas = useMemo(() => {
        return products
            .filter((p: Product) => (p.gap_market || 0) >= 1)
            .sort((a: Product, b: Product) => (b.gap_market || 0) - (a.gap_market || 0))
            .slice(0, 4);
    }, [products]);

    useEffect(() => {
        const eventSource = new EventSource("/api/events");
        eventSource.onmessage = (event: MessageEvent) => {
            try {
                const data = JSON.parse(event.data);
                // Si el evento dice que hay que refrescar (oportunidad o log importante)
                if (data.refreshProducts) {
                    // Re-fetch de la API de radar para obtener lo último
                    fetch("/api/radar?limit=100")
                        .then(res => res.json())
                        .then(d => {
                            if (d.success) setProducts((prev: Product[]) => {
                                // Mergear evitando duplicados
                                const newItems = d.items.filter((ni: Product) => !prev.find((p: Product) => p.url === ni.url));
                                return [...newItems, ...prev];
                            });
                        });
                }

                // Si el evento trae un producto directamente
                if (data.type === 'opportunity' && data.product) {
                    setProducts((prev: Product[]) => {
                        if (prev.find((p: Product) => p.url === data.product.url)) return prev;
                        return [data.product, ...prev];
                    });
                }
            } catch (e) { console.error("Real-time error:", e); }
        };
        return () => eventSource.close();
    }, []);

    // UI State for Sidebar Accordions
    const [openSections, setOpenSections] = useState<string[]>(["categories", "radar"]);

    const toggleSection = (section: string) => {
        setOpenSections((prev: string[]) =>
            prev.includes(section) ? prev.filter((s: string) => s !== section) : [...prev, section]
        );
    };

    const SidebarContent = () => (
        <div className="flex flex-col h-full bg-[#020617] text-slate-300 select-none">
            {/* Logo / Header */}
            <div className="p-6 border-b border-white/5 flex items-center justify-between bg-slate-900/50 backdrop-blur-3xl sticky top-0 z-20">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-red-600 rounded-xl flex items-center justify-center text-white shadow-[0_0_15px_rgba(220,38,38,0.5)] border border-red-500/50">
                        <Bomb size={20} fill="white" className="animate-pulse" />
                    </div>
                    <div>
                        <span className="text-sm font-black text-white uppercase tracking-tighter block leading-none underline decoration-red-600">SOSA-OS</span>
                        <span className="text-[8px] font-bold text-red-500/80 uppercase tracking-widest block mt-1">RADAR ARBITRAJE</span>
                    </div>
                </div>
                <button onClick={() => setIsSidebarOpen(false)} className="hidden lg:block text-slate-500 hover:text-white transition-colors p-2 hover:bg-white/5 rounded-xl">
                    <PanelLeftClose size={20} />
                </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-hide custom-scrollbar">
                {/* Search - Ultra Sleek */}
                <div className="relative group px-2">
                    <Search className="absolute left-6 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-red-500 transition-colors" size={14} />
                    <input
                        type="text"
                        placeholder="ESCANEAR MERCADO..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full bg-white/5 border border-white/10 py-3 pl-12 pr-4 rounded-2xl text-[11px] font-bold text-white outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500/50 transition-all font-mono placeholder:text-slate-600 tracking-wider"
                    />
                </div>

                <nav className="space-y-2">
                    {/* ACCORDION: RADAR FILTERS */}
                    <div className="px-2">
                        <button
                            onClick={() => toggleSection("radar")}
                            className="w-full flex items-center justify-between p-3 rounded-xl hover:bg-white/5 transition-colors group border border-transparent hover:border-white/5"
                        >
                            <div className="flex items-center gap-3">
                                <Zap size={16} className={cn("transition-colors", openSections.includes("radar") ? "text-red-500" : "text-slate-500")} />
                                <span className="text-[11px] font-black uppercase tracking-wider">Configuración Radar</span>
                            </div>
                            <ChevronDown size={14} className={cn("transition-transform duration-300", openSections.includes("radar") ? "rotate-180" : "rotate-0")} />
                        </button>

                        {openSections.includes("radar") && (
                            <div className="mt-4 px-2 space-y-6 animate-in fade-in slide-in-from-top-2 duration-300">
                                {/* Profit Filter % */}
                                <div className="space-y-3">
                                    <div className="flex items-center justify-between">
                                        <label className="text-[10px] font-black text-red-500 uppercase tracking-widest flex items-center gap-2">
                                            <TrendingUp size={12} /> Margen Ganancia (%)
                                        </label>
                                        <span className="text-[11px] font-mono font-black text-white bg-red-600 px-2.5 py-1 rounded-md shadow-[0_0_10px_rgba(220,38,38,0.3)]">+{minMarginPct}%</span>
                                    </div>
                                    <input
                                        type="range"
                                        min="0"
                                        max="100"
                                        step="1"
                                        value={minMarginPct}
                                        onChange={(e) => setMinMarginPct(Number(e.target.value))}
                                        className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-red-600"
                                    />
                                </div>

                                {/* Profit Filter ARS */}
                                <div className="space-y-3">
                                    <div className="flex items-center justify-between">
                                        <label className="text-[10px] font-black text-emerald-500 uppercase tracking-widest flex items-center gap-2">
                                            <DollarSign size={12} /> Ahorro Mínimo (ARS)
                                        </label>
                                        <span className="text-[11px] font-mono font-black text-white bg-emerald-600 px-2.5 py-1 rounded-md shadow-[0_0_10px_rgba(5,150,105,0.3)]">${(minProfit / 1000).toFixed(0)}k</span>
                                    </div>
                                    <input
                                        type="range"
                                        min="0"
                                        max="500000"
                                        step="5000"
                                        value={minProfit}
                                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setMinProfit(Number(e.target.value))}
                                        className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                                    />
                                </div>
                            </div>
                        )}
                    </div>

                    {/* ACCORDION: CATEGORIAS */}
                    <div className="px-2">
                        <button
                            onClick={() => toggleSection("categories")}
                            className="w-full flex items-center justify-between p-3 rounded-xl hover:bg-white/5 transition-colors group"
                        >
                            <div className="flex items-center gap-3">
                                <LayoutGrid size={16} className={cn("transition-colors", openSections.includes("categories") ? "text-blue-500" : "text-slate-500")} />
                                <span className="text-[11px] font-black uppercase tracking-wider">Filtro Categorías</span>
                            </div>
                            <ChevronDown size={14} className={cn("transition-transform duration-300", openSections.includes("categories") ? "rotate-180" : "rotate-0")} />
                        </button>

                        {openSections.includes("categories") && (
                            <div className="mt-2 ml-4 pl-3 border-l border-white/5 space-y-1 animate-in fade-in slide-in-from-top-1 duration-200">
                                <button
                                    onClick={() => setSelectedCategory(null)}
                                    className={cn(
                                        "w-full text-left px-3 py-2 rounded-lg text-[11px] font-bold transition-all",
                                        !selectedCategory ? "text-white bg-white/10 border border-white/20" : "text-slate-500 hover:text-white hover:bg-white/5"
                                    )}
                                >
                                    Escáner Global
                                </button>
                                {mainCategories.map(cat => (
                                    <button
                                        key={cat}
                                        onClick={() => setSelectedCategory(cat)}
                                        className={cn(
                                            "w-full text-left px-3 py-2.5 rounded-lg text-[11px] font-bold transition-all flex items-center justify-between",
                                            selectedCategory === cat ? "text-white bg-white/10 border border-white/20" : "text-slate-500 hover:text-white hover:bg-white/5"
                                        )}
                                    >
                                        <span>{cat}</span>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                </nav>
            </div>

            {/* System Status / SOSA-OS Footer */}
            <div className="p-4 bg-white/5 border-t border-white/5">
                <div className="flex items-center gap-4">
                    <div className="relative">
                        <div className="w-10 h-10 rounded-2xl bg-slate-800 flex items-center justify-center text-[11px] font-black border border-white/10 text-red-500 shadow-inner">AL</div>
                        <div className="absolute -bottom-1 -right-1 w-3.5 h-3.5 bg-red-500 rounded-full border-2 border-[#020617] animate-pulse" />
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-[11px] font-black text-white truncate font-mono tracking-tighter">ARCHITECT_MODE_ON</p>
                        <div className="flex items-center gap-1.5 mt-0.5">
                            <div className="w-1 h-1 bg-red-500 rounded-full animate-ping" />
                            <p className="text-[8px] font-bold text-red-500/60 uppercase tracking-widest">SOSA-OS ACTIVE</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );

    return (
        <div className="flex w-full h-[calc(100vh-140px)] overflow-hidden bg-[#0a0a0a]">
            {/* Sidebar Desktop Compacto */}
            {isSidebarOpen ? (
                <aside className="hidden lg:block w-80 flex-shrink-0 h-full border-r border-white/5 z-50 transition-all duration-500">
                    <SidebarContent />
                </aside>
            ) : null}

            {/* Mobile Menu */}
            {isMobileMenuOpen && (
                <div className="fixed inset-0 z-[100] bg-black/80 backdrop-blur-sm lg:hidden" onClick={() => setIsMobileMenuOpen(false)}>
                    <div className="absolute left-0 top-0 bottom-0 w-72 bg-[#020617]" onClick={e => e.stopPropagation()}>
                        <SidebarContent />
                    </div>
                </div>
            )}

            {/* Main Area */}
            <main className="flex-1 flex flex-col h-full bg-[#030712] min-w-0 transition-all duration-300 relative">
                {/* Neon Overlay Grids */}
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none"></div>

                {/* Internal Toolbar Compacto */}
                <div className="bg-slate-950/80 backdrop-blur-3xl px-8 py-5 border-b border-white/5 flex items-center justify-between z-20 sticky top-0">
                    <div className="flex items-center gap-6">
                        {!isSidebarOpen && (
                            <button
                                onClick={() => setIsSidebarOpen(true)}
                                className="hidden lg:flex p-2.5 bg-red-600 text-white rounded-xl hover:scale-105 active:scale-95 transition-all shadow-[0_0_15px_rgba(220,38,38,0.4)]"
                            >
                                <PanelLeftOpen size={18} />
                            </button>
                        )}
                        <button
                            onClick={() => setIsMobileMenuOpen(true)}
                            className="lg:hidden p-2.5 bg-white/5 text-slate-400 rounded-xl"
                        >
                            <Menu size={18} />
                        </button>
                        <div className="flex items-center gap-6 border-l border-white/10 pl-6">
                            <div className="flex flex-col">
                                <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest leading-none">SEÑALES ACTUALES</span>
                                <div className="flex items-center gap-2 mt-1">
                                    <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(239,68,68,0.8)]" />
                                    <span className="text-sm font-black text-white uppercase tracking-tighter font-mono italic">
                                        {filteredProducts.length} OBJECTOS_DETECTADOS
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <select
                            value={sort}
                            onChange={(e) => setSort(e.target.value)}
                            className="bg-white/5 border border-white/10 px-4 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest outline-none cursor-pointer hover:border-red-500/50 transition-all text-white font-mono"
                        >
                            <option value="opportunity">ORDENAR_MARGEN</option>
                            <option value="price_asc">ORDENAR_PRECIO</option>
                        </select>
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto custom-scrollbar scroll-smooth">
                    {/* ZONA DE BOMBAS - NEON STYLE */}
                    {bombas.length > 0 && !selectedCategory && !search && (
                        <div className="px-8 pt-10 pb-16 relative">
                            <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-b from-red-600/5 to-transparent pointer-events-none"></div>

                            <div className="flex items-center justify-between mb-10 relative">
                                <div className="flex items-center gap-4">
                                    <div className="w-16 h-16 bg-red-600 rounded-[2rem] flex items-center justify-center text-white shadow-[0_0_40px_rgba(220,38,38,0.4)] border-2 border-red-400/30 rotate-3 animate-pulse">
                                        <Bomb size={32} />
                                    </div>
                                    <div className="space-y-1">
                                        <h2 className="text-4xl font-black text-white tracking-tighter uppercase leading-none italic">
                                            ZONA DE BOMBAS
                                        </h2>
                                        <div className="flex items-center gap-3">
                                            <p className="text-red-500 font-mono font-black text-[11px] uppercase tracking-[0.2em] flex items-center gap-2 bg-red-600/10 px-4 py-1.5 rounded-full border border-red-600/30">
                                                <Flame size={14} /> DETECCIÓN CRÍTICA SOSA-OS
                                            </p>
                                        </div>
                                    </div>
                                </div>
                                <div className="text-right hidden sm:block">
                                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest block font-mono">ENLACE_DE_DATOS</span>
                                    <span className="text-lg font-black text-white font-mono tracking-tighter italic shadow-inner">STREAM_V2_ACTIVO</span>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 relative z-10">
                                {bombas.map((p) => (
                                    <div key={p.url || p.name} className="transform hover:scale-[1.02] transition-transform duration-500 group">
                                        <div className="absolute -inset-0.5 bg-gradient-to-r from-red-600 to-amber-500 rounded-[26px] blur opacity-40 group-hover:opacity-75 transition duration-500"></div>
                                        <ProductCard product={p} isBomb={true} />
                                    </div>
                                ))}
                            </div>

                            <div className="h-px bg-gradient-to-r from-transparent via-red-900/50 to-transparent w-full mt-20" />
                        </div>
                    )}

                    {/* Content Grid */}
                    <div className="px-8 pb-32">
                        <div className="flex items-center justify-between mb-10">
                            <div className="flex items-center gap-3">
                                <div className="w-1.5 h-6 bg-blue-600 rounded-full"></div>
                                <h3 className="text-base font-black text-white uppercase tracking-widest font-mono italic">RADAR_DE_BARRIDO</h3>
                            </div>
                            <div className="flex items-center gap-4 text-[10px] font-mono text-slate-500 uppercase tracking-widest">
                                <span>Filtros: {selectedCategory || "TOTAL"}</span>
                                <span className="w-1 h-1 bg-slate-700 rounded-full"></span>
                                <span>Margen: +{minMarginPct}%</span>
                            </div>
                        </div>

                        {filteredProducts.length > 0 ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-8">
                                {filteredProducts.map((p) => (
                                    <div key={p.url || p.name} className="h-auto transform transition-all duration-300">
                                        <ProductCard product={p} />
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="py-40 flex flex-col items-center justify-center bg-slate-900/40 rounded-[3rem] border-2 border-dashed border-white/5 mx-auto max-w-4xl">
                                <div className="w-20 h-20 bg-slate-800 rounded-full flex items-center justify-center mb-6 shadow-2xl">
                                    <AlertCircle size={40} className="text-slate-600" />
                                </div>
                                <h3 className="text-lg font-black text-white uppercase tracking-[0.3em] font-mono mb-2">SEÑAL_PERDIDA</h3>
                                <p className="text-slate-500 font-bold text-xs uppercase tracking-widest">Ajustá los parámetros del radar</p>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}
