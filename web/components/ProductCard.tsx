"use client";

import React, { useState } from "react";
import { ExternalLink, Store, TrendingUp, AlertTriangle, BarChart2, ChevronDown, ChevronUp, ShieldCheck, Zap } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { PriceEvolutionChart } from "./PriceChart";
import { cn } from "@/lib/utils";

export interface Product {
  name: string;
  brand: string;
  price: number;
  list_price: number;
  discount_pct: number;
  url: string;
  img: string;
  store: string;
  category: string;
  competitors?: { store: string; price: number }[];
  market_min?: number | null;
  z_score?: number;
  verified?: boolean;
}

export const ProductCard = ({ product }: { product: Product }) => {
  const [showAnalysis, setShowAnalysis] = useState(false);

  const formatPrice = (p: number) => {
    return new Intl.NumberFormat("es-AR", {
      style: "currency",
      currency: "ARS",
      maximumFractionDigits: 0,
    }).format(p || 0);
  };

  const discount = Math.round(product.discount_pct || 0);
  const zScore = product.z_score || 0;
  const isGlitch = discount > 50 || zScore < -2.5;

  const profitPercentage = product.market_min ? ((product.market_min - product.price) / product.price) * 100 : 0;

  // Consolidar todos los puntos de datos de mercado (esta oferta + competidores)
  const marketOverview = [
    { store: product.store, price: product.price, isCurrent: true, url: product.url },
    ...(product.competitors || []).map(c => ({ ...c, isCurrent: false, url: '#' })) // En prod vendría la URL real
  ].sort((a, b) => a.price - b.price);

  return (
    <div className={cn(
      "group bg-white rounded-3xl border border-slate-200 overflow-hidden transition-all duration-500 pro-shadow pro-shadow-hover flex flex-col h-full",
      isGlitch && "border-red-200 ring-4 ring-red-50"
    )}>
      {/* Media Section */}
      <div className="relative aspect-square bg-white p-8 flex items-center justify-center overflow-hidden border-b border-slate-100">
        <img
          src={product.img || "/placeholder.png"}
          alt={product.name}
          className="max-h-full max-w-full object-contain transition-transform duration-700 group-hover:scale-110"
          onError={(e) => (e.currentTarget.src = "https://placehold.co/400x300?text=Sin+Imagen")}
        />

        {/* Badges Flotantes */}
        <div className="absolute top-5 left-5 flex flex-col gap-2">
          <div className="bg-slate-900 text-white px-3 py-1.5 rounded-full flex items-center gap-2 shadow-xl shadow-slate-200">
            <Store size={12} />
            <span className="text-[10px] font-black uppercase tracking-widest">{product.store}</span>
          </div>
        </div>

        {isGlitch && (
          <div className="absolute top-5 right-5 animate-bounce">
            <div className="bg-red-600 text-white text-[10px] font-black uppercase px-3 py-1.5 rounded-full shadow-xl flex items-center gap-2">
              <Zap size={12} fill="white" /> GLITCH
            </div>
          </div>
        )}
      </div>

      {/* Content Section */}
      <div className="p-6 flex flex-col flex-1">
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">{product.brand || "E-commerce Intelligence"}</span>
            {product.verified && (
              <div className="flex items-center gap-1 text-[9px] font-black text-emerald-600 bg-emerald-50 px-2 py-1 rounded-md border border-emerald-100">
                <ShieldCheck size={10} /> VERIFICADO
              </div>
            )}
          </div>
          <h3 className="text-base font-bold text-slate-900 line-clamp-2 leading-snug min-h-[2.8rem]">
            {product.name}
          </h3>
        </div>

        {/* Intelligence Hub */}
        <div className={cn(
          "rounded-2xl border transition-all duration-500 mb-6",
          showAnalysis ? "bg-slate-900 border-slate-800 p-5" : "bg-slate-50 border-slate-100 p-4"
        )}>
          <div className="flex justify-between items-center mb-3">
            <div className="flex items-center gap-2">
              <span className={cn("text-[10px] font-black uppercase tracking-wider", showAnalysis ? "text-slate-400" : "text-slate-500")}>
                {showAnalysis ? "Análisis de Arbitraje" : "Rastreador de Mercado"}
              </span>
            </div>
            <button
              onClick={() => setShowAnalysis(!showAnalysis)}
              className={cn(
                "text-[10px] font-black uppercase tracking-widest flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all",
                showAnalysis ? "bg-white text-slate-900" : "bg-white border border-slate-200 text-blue-600 shadow-sm"
              )}
            >
              {showAnalysis ? <ChevronUp size={12} /> : <BarChart2 size={12} />}
              {showAnalysis ? "Cerrar" : "Comparar Tiendas"}
            </button>
          </div>

          <AnimatePresence mode="wait">
            {showAnalysis ? (
              <motion.div
                key="analysis"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="space-y-4"
              >
                <div className="space-y-2">
                  {marketOverview.map((item, i) => (
                    <div key={i} className={cn(
                      "flex items-center justify-between p-2.5 rounded-xl border transition-all",
                      item.isCurrent
                        ? "bg-blue-600/10 border-blue-500/30 text-white"
                        : "bg-white/5 border-white/5 text-slate-400"
                    )}>
                      <div className="flex items-center gap-3">
                        <span className="text-[10px] font-black text-slate-500 w-4">{i + 1}</span>
                        <span className={cn("text-xs font-bold", item.isCurrent ? "text-blue-400" : "text-slate-200")}>{item.store}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className={cn("text-xs font-black", item.isCurrent ? "text-white" : "text-slate-300")}>
                          {formatPrice(item.price)}
                        </span>
                        {item.isCurrent && <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />}
                      </div>
                    </div>
                  ))}
                </div>
                <p className="text-[9px] text-slate-500 font-medium leading-relaxed italic">
                  * Datos actualizados hace minutos. Haz clic en "Ver Tienda" para comprobar stock real.
                </p>
              </motion.div>
            ) : (
              <div className="flex items-center justify-between">
                <div className="flex flex-col">
                  <span className="text-[9px] font-black text-slate-400 uppercase tracking-tighter">Promedio Mercado</span>
                  <span className="text-sm font-bold text-slate-700">
                    {formatPrice(product.market_min || product.price * 1.2)}
                  </span>
                </div>
                <div className="h-8 w-px bg-slate-200" />
                <div className="flex flex-col items-end">
                  <span className="text-[9px] font-black text-slate-400 uppercase tracking-tighter">Tiendas Activas</span>
                  <span className="text-sm font-bold text-slate-700">
                    {marketOverview.length} Fuentes
                  </span>
                </div>
              </div>
            )}
          </AnimatePresence>
        </div>

        {/* Pricing & Call to Action */}
        <div className="mt-auto">
          <div className="flex items-end justify-between mb-5">
            <div className="flex flex-col">
              <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Mejor Precio Hoy</span>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-black text-slate-900 tracking-tighter leading-none">
                  {formatPrice(product.price)}
                </span>
                {product.list_price > product.price && (
                  <span className="text-xs text-slate-400 line-through font-bold">
                    {formatPrice(product.list_price)}
                  </span>
                )}
              </div>
            </div>
            {profitPercentage > 0 && (
              <div className="bg-emerald-50 px-3 py-2 rounded-2xl flex flex-col items-end border border-emerald-100">
                <span className="text-[8px] font-black text-emerald-600 uppercase tracking-widest">Ahorro Neto</span>
                <span className="text-lg font-black text-emerald-600 leading-none">
                  {profitPercentage.toFixed(0)}%
                </span>
              </div>
            )}
          </div>

          <div className="flex gap-2">
            <a
              href={product.url}
              target="_blank"
              rel="noopener noreferrer"
              className={cn(
                "flex-1 py-4 rounded-2xl text-[10px] font-black uppercase tracking-[0.15em] transition-all duration-300 flex items-center justify-center gap-2 shadow-lg",
                isGlitch
                  ? "bg-red-600 text-white hover:bg-red-700 shadow-red-200"
                  : "bg-slate-900 text-white hover:bg-slate-800 shadow-slate-200"
              )}
            >
              Ver en {product.store}
              <ExternalLink size={14} />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
