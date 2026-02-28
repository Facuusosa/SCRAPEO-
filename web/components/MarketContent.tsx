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

    const activeBrands = useMemo(() => {
        const brands = new Set<string>();
        if (products && Array.isArray(products)) {
            products.forEach(p => { if (p?.brand) brands.add(p.brand); });
        }
        return Array.from(brands).sort().slice(0, 30); // Limite para no saturar
    }, [products]);

    const [selectedBrands, setSelectedBrands] = useState<string[]>([]);

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

                const matchesBrand = selectedBrands.length === 0 || selectedBrands.includes(p.brand);
                if (!matchesBrand) return false;

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

    // OPORTUNIDADES BOMBA (Gap > 20% y validado)
    const bombas = useMemo(() => {
        return products
            .filter(p => (p.gap_market || 0) >= 18) // Bajamos un pelín el umbral para asegurar volumen
            .sort((a, b) => (b.gap_market || 0) - (a.gap_market || 0))
            .slice(0, 100); // 100 materiales mejores como pidió el usuario
    }, [products]);

    useEffect(() => {
        const eventSource = new EventSource("/api/events");
        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                // Si el evento dice que hay que refrescar (oportunidad o log importante)
                if (data.refreshProducts) {
                    // Re-fetch de la API de radar para obtener lo último
                    fetch("/api/radar?limit=100")
                        .then(res => res.json())
                        .then(d => {
                            if (d.success) setProducts(prev => {
                                // Mergear evitando duplicados
                                const newItems = d.items.filter((ni: any) => !prev.find(p => p.url === ni.url));
                                return [...newItems, ...prev];
                            });
                        });
                }

                // Si el evento trae un producto directamente
                if (data.type === 'opportunity' && data.product) {
                    setProducts(prev => {
                        if (prev.find(p => p.url === data.product.url)) return prev;
                        return [data.product, ...prev];
                    });
                }
            } catch (e) { console.error("Real-time error:", e); }
        };
        return () => eventSource.close();
    }, []);

    // UI State for Sidebar Accordions
    const [openSections, setOpenSections] = useState<string[]>(["categories", "bombas"]);

    const toggleSection = (section: string) => {
        setOpenSections(prev =>
            prev.includes(section) ? prev.filter(s => s !== section) : [...prev, section]
        );
    };

    const SidebarContent = () => (
        <div className="flex flex-col h-full bg-[#0f172a] text-slate-300 select-none">
            {/* Logo / Header */}
            <div className="p-6 border-b border-slate-800/50 flex items-center justify-between bg-[#1e293b]/20 backdrop-blur-xl sticky top-0 z-20">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
                        <Zap size={16} fill="white" />
                    </div>
                    <div>
                        <span className="text-xs font-black text-white uppercase tracking-tighter block leading-none">Odiseo</span>
                        <span className="text-[8px] font-bold text-slate-500 uppercase tracking-widest block mt-0.5">Market Pro</span>
                    </div>
                </div>
                <button onClick={() => setIsSidebarOpen(false)} className="hidden lg:block text-slate-500 hover:text-white transition-colors p-1.5 hover:bg-slate-800 rounded-lg">
                    <PanelLeftClose size={18} />
                </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide custom-scrollbar">
                {/* Search - Ultra Sleek */}
                <div className="relative group px-2">
                    <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-blue-400 transition-colors" size={12} />
                    <input
                        type="text"
                        placeholder="Filtrar mercado..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full bg-slate-800/50 border border-slate-700/50 py-2.5 pl-10 pr-4 rounded-xl text-[10px] font-bold text-white outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all font-geist placeholder:text-slate-600"
                    />
                </div>

                <nav className="space-y-1">
                    {/* ACCORDION: CATEGORIAS */}
                    <div className="px-2">
                        <button
                            onClick={() => toggleSection("categories")}
                            className="w-full flex items-center justify-between p-2 rounded-lg hover:bg-slate-800/50 transition-colors group"
                        >
                            <div className="flex items-center gap-3">
                                <LayoutGrid size={14} className={cn("transition-colors", openSections.includes("categories") ? "text-blue-400" : "text-slate-500")} />
                                <span className="text-[10px] font-black uppercase tracking-wider">Explorar Categorías</span>
                            </div>
                            <ChevronDown size={12} className={cn("transition-transform duration-300", openSections.includes("categories") ? "rotate-180" : "rotate-0")} />
                        </button>

                        {openSections.includes("categories") && (
                            <div className="mt-1 ml-4 pl-3 border-l border-slate-800 space-y-0.5 animate-in fade-in slide-in-from-top-1 duration-200">
                                <button
                                    onClick={() => setSelectedCategory(null)}
                                    className={cn(
                                        "w-full text-left px-3 py-1.5 rounded-md text-[10px] font-bold transition-all",
                                        !selectedCategory ? "text-blue-400 bg-blue-500/10" : "text-slate-400 hover:text-white hover:bg-slate-800"
                                    )}
                                >
                                    Catálogo Completo
                                </button>
                                {mainCategories.map(cat => (
                                    <button
                                        key={cat}
                                        onClick={() => setSelectedCategory(cat)}
                                        className={cn(
                                            "w-full text-left px-3 py-2.5 rounded-md text-[11px] font-bold transition-all flex items-center justify-between",
                                            selectedCategory === cat ? "text-blue-400 bg-blue-500/10" : "text-slate-500 hover:text-white hover:bg-slate-800"
                                        )}
                                    >
                                        <span>{cat}</span>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* ACCORDION: MARCAS */}
                    <div className="px-2">
                        <button
                            onClick={() => toggleSection("brands")}
                            className="w-full flex items-center justify-between p-2 rounded-lg hover:bg-slate-800/50 transition-colors group"
                        >
                            <div className="flex items-center gap-3">
                                <Tag size={14} className={cn("transition-colors", openSections.includes("brands") ? "text-blue-400" : "text-slate-500")} />
                                <span className="text-[10px] font-black uppercase tracking-wider">Marcas Pro</span>
                            </div>
                            <ChevronDown size={12} className={cn("transition-transform duration-300", openSections.includes("brands") ? "rotate-180" : "rotate-0")} />
                        </button>

                        {openSections.includes("brands") && (
                            <div className="mt-2 grid grid-cols-2 gap-1.5 animate-in fade-in slide-in-from-top-1 duration-200">
                                {activeBrands.map(brand => (
                                    <button
                                        key={brand}
                                        onClick={() => {
                                            setSelectedBrands(prev =>
                                                prev.includes(brand) ? prev.filter(b => b !== brand) : [...prev, brand]
                                            );
                                        }}
                                        className={cn(
                                            "px-2 py-2 rounded-lg text-[8px] font-black transition-all border text-center truncate uppercase tracking-tighter",
                                            selectedBrands.includes(brand)
                                                ? "bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-500/20"
                                                : "bg-[#1e293b]/40 border-slate-700/50 text-slate-500 hover:border-slate-500 hover:text-slate-300"
                                        )}
                                    >
                                        {brand}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* ACCORDION: TIENDAS */}
                    <div className="px-2">
                        <button
                            onClick={() => toggleSection("stores")}
                            className="w-full flex items-center justify-between p-2 rounded-lg hover:bg-slate-800/50 transition-colors group"
                        >
                            <div className="flex items-center gap-3">
                                <Store size={14} className={cn("transition-colors", openSections.includes("stores") ? "text-blue-400" : "text-slate-500")} />
                                <span className="text-[10px] font-black uppercase tracking-wider">Central de Tiendas</span>
                            </div>
                            <ChevronDown size={12} className={cn("transition-transform duration-300", openSections.includes("stores") ? "rotate-180" : "rotate-0")} />
                        </button>

                        {openSections.includes("stores") && (
                            <div className="mt-1 space-y-1 animate-in fade-in slide-in-from-top-1 duration-200">
                                {activeStores.map(store => (
                                    <button
                                        key={store}
                                        onClick={() => {
                                            setSelectedStores(prev =>
                                                prev.includes(store) ? prev.filter(s => s !== store) : [...prev, store]
                                            );
                                        }}
                                        className={cn(
                                            "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-[10px] font-bold transition-all text-left group",
                                            selectedStores.includes(store)
                                                ? "bg-slate-800 text-white"
                                                : "text-slate-500 hover:bg-slate-800/50 hover:text-slate-300"
                                        )}
                                    >
                                        <div className={cn(
                                            "w-2 h-2 rounded-full",
                                            selectedStores.includes(store) ? "bg-blue-500 animate-pulse ring-4 ring-blue-500/20" : "bg-slate-700"
                                        )} />
                                        <span>{store}</span>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                </nav>

                {/* Margen Slider simulated */}
                <div className="pt-6 border-t border-slate-800 px-2 space-y-4">
                    <div className="flex items-center justify-between">
                        <label className="text-[9px] font-black text-emerald-500 uppercase tracking-widest flex items-center gap-2">
                            <DollarSign size={10} /> Filtro de Ganancia
                        </label>
                        <span className="text-[10px] font-mono font-black text-emerald-400">+{minProfit}</span>
                    </div>
                    <input
                        type="range"
                        min="0"
                        max="500000"
                        step="5000"
                        value={minProfit}
                        onChange={(e) => setMinProfit(Number(e.target.value))}
                        className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                    />
                </div>
            </div>

            {/* User Profile / Status */}
            <div className="p-4 bg-[#1e293b]/40 border-t border-slate-800/50">
                <div className="flex items-center gap-3">
                    <div className="relative">
                        <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-[10px] font-bold border border-slate-600">FA</div>
                        <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-500 rounded-full border-2 border-[#0f172a]" />
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-[10px] font-black text-white truncate">Usuario Pro</p>
                        <p className="text-[8px] font-bold text-slate-500 uppercase tracking-widest">Sincronizado</p>
                    </div>
                </div>
            </div>
        </div>
    );

    return (
        <div className="flex w-full h-[calc(100vh-140px)] overflow-hidden bg-[#f8fafc]">
            {/* Sidebar Desktop Compacto */}
            {isSidebarOpen ? (
                <aside className="hidden lg:block w-72 flex-shrink-0 h-full border-r border-slate-200 z-50 transition-all duration-300 shadow-2xl">
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
                        <div className="flex items-center gap-4 border-l border-slate-200 pl-4">
                            <div className="flex flex-col">
                                <span className="text-[8px] font-black text-slate-400 uppercase tracking-widest">Estado</span>
                                <div className="flex items-center gap-1.5">
                                    <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
                                    <span className="text-[10px] font-black text-slate-900 uppercase tracking-tighter">
                                        {filteredProducts.length} Activos
                                    </span>
                                </div>
                            </div>
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

                {/* Bombas Section */}
                {bombas.length > 0 && !selectedCategory && !search && (
                    <div className="px-8 pt-8">
                        <div className="flex items-center justify-between mb-6">
                            <div className="flex items-center gap-3">
                                <div className="w-12 h-12 bg-red-600 rounded-2xl flex items-center justify-center text-white shadow-2xl shadow-red-500/30 animate-pulse">
                                    <Bomb size={24} />
                                </div>
                                <div>
                                    <h2 className="text-2xl font-black text-slate-900 tracking-tight uppercase leading-none mb-1.5">Arbitraje Radar (Top 100)</h2>
                                    <p className="text-red-600 font-black text-[10px] uppercase tracking-widest flex items-center gap-2 bg-red-50 px-3 py-1 rounded-full w-fit">
                                        <Flame size={12} /> Oportunidades críticas de alto margen
                                    </p>
                                </div>
                            </div>
                            <div className="text-right">
                                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">Actualizado</span>
                                <span className="text-xs font-bold text-slate-900 font-mono">Tiempo Real (Stream)</span>
                            </div>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-6">
                            {bombas.map((p, i) => (
                                <div key={i} className="h-auto">
                                    <ProductCard product={p} />
                                </div>
                            ))}
                        </div>
                        <div className="h-px bg-slate-200 w-full mt-16" />
                    </div>
                )}

                {/* Content Grid */}
                <div className="flex-1 overflow-y-auto p-8 scrollbar-hide">
                    <div className="flex items-center justify-between mb-8">
                        <div className="flex items-center gap-2">
                            <TrendingUp size={16} className="text-blue-600" />
                            <h3 className="text-xs font-black text-slate-900 uppercase tracking-widest">Listado de Mercado</h3>
                        </div>
                    </div>
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
