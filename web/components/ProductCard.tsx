"use client";

import React, { useState } from "react";
import { ExternalLink, Store, TrendingUp, AlertTriangle, BarChart2, ChevronDown, ChevronUp, ShieldCheck } from "lucide-react";
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
  const [showChart, setShowChart] = useState(false);

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

  return (
    <div className={cn(
      "group bg-white rounded-2xl border border-slate-200 overflow-hidden transition-all duration-300 pro-shadow pro-shadow-hover flex flex-col h-full",
      isGlitch && "border-red-200 bg-red-50/30"
    )}>
      {/* Header Imagen */}
      <div className="relative aspect-video bg-slate-50 p-6 flex items-center justify-center overflow-hidden border-b border-slate-100">
        <img
          src={product.img || "/placeholder.png"}
          alt={product.name}
          className="max-h-full max-w-full object-contain mix-blend-multiply group-hover:scale-105 transition-transform duration-500"
          onError={(e) => (e.currentTarget.src = "https://placehold.co/400x300?text=Sin+Imagen")}
        />

        {/* Badges */}
        <div className="absolute top-4 left-4 flex flex-col gap-2">
          <div className="bg-white/90 backdrop-blur px-2 py-1 rounded-lg border border-slate-200 flex items-center gap-1.5 shadow-sm">
            <Store size={12} className="text-slate-900" />
            <span className="text-[10px] font-bold text-slate-900 uppercase tracking-tight">{product.store}</span>
          </div>
        </div>

        {isGlitch && (
          <div className="absolute top-4 right-4 animate-pulse">
            <div className="bg-red-600 text-white text-[9px] font-black uppercase px-2 py-1 rounded shadow-lg flex items-center gap-1">
              <AlertTriangle size={10} /> GLITCH DETECTADO
            </div>
          </div>
        )}
      </div>

      {/* Contenido */}
      <div className="p-5 flex flex-col flex-1">
        <div className="mb-3">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{product.brand || "Genérico"}</span>
            <div className="h-px bg-slate-100 flex-1" />
            {product.verified && (
              <span className="text-[9px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-100 flex items-center gap-1">
                <ShieldCheck size={10} /> VERIFICADO
              </span>
            )}
          </div>
          <h3 className="text-sm font-bold text-slate-800 line-clamp-2 leading-tight min-h-[2.5rem]">
            {product.name}
          </h3>
        </div>

        {/* Info de Mercado */}
        <div className="bg-slate-50 rounded-xl p-3 border border-slate-100 mb-4">
          <div className="flex justify-between items-center mb-2">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">Inteligencia</span>
              {zScore !== 0 && (
                <span className={cn(
                  "text-[9px] font-mono font-bold px-1.5 py-0.5 rounded",
                  zScore < -2.0 ? "bg-red-100 text-red-700" : "bg-slate-200 text-slate-600"
                )}>
                  Z: {zScore.toFixed(2)}σ
                </span>
              )}
            </div>
            <button
              onClick={() => setShowChart(!showChart)}
              className="text-[10px] font-bold text-blue-600 hover:text-blue-700 uppercase flex items-center gap-1"
            >
              {showChart ? <ChevronDown size={12} /> : <BarChart2 size={12} />}
              {showChart ? "Cerrar" : "Análisis"}
            </button>
          </div>

          <AnimatePresence mode="wait">
            {showChart ? (
              <motion.div
                key="chart"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
              >
                <PriceEvolutionChart currentPrice={product.price} competitors={product.competitors} marketMin={product.market_min} />
              </motion.div>
            ) : (
              <div className="space-y-1">
                {product.competitors && product.competitors.length > 0 ? (
                  product.competitors.slice(0, 2).map((comp, i) => (
                    <div key={i} className="flex justify-between items-center">
                      <span className="text-[11px] text-slate-500">{comp.store}</span>
                      <span className="text-[11px] font-bold text-slate-700">{formatPrice(comp.price)}</span>
                    </div>
                  ))
                ) : (
                  <span className="text-[10px] text-slate-400 italic">Sin datos de competencia registrados</span>
                )}
              </div>
            )}
          </AnimatePresence>
        </div>

        {/* Precios */}
        <div className="mt-auto pt-2">
          <div className="flex items-end justify-between mb-4">
            <div className="flex flex-col">
              <span className="text-[10px] font-bold text-slate-400 uppercase">Precio Hoy</span>
              <span className="text-xl font-black text-slate-900 leading-none">
                {formatPrice(product.price)}
              </span>
            </div>
            {profitPercentage > 0 && (
              <div className="flex flex-col items-end">
                <span className="text-[10px] font-bold text-emerald-600 uppercase">Margen vs Mercado</span>
                <span className="text-lg font-black text-emerald-600 leading-none flex items-center gap-1">
                  <TrendingUp size={16} />
                  {profitPercentage.toFixed(0)}%
                </span>
              </div>
            )}
          </div>

          <a
            href={product.url}
            target="_blank"
            rel="noopener noreferrer"
            className={cn(
              "w-full py-3 rounded-xl text-xs font-black uppercase tracking-widest transition-all flex items-center justify-center gap-2",
              isGlitch
                ? "bg-red-600 text-white hover:bg-red-700 shadow-lg shadow-red-200"
                : "bg-slate-900 text-white hover:bg-slate-800 shadow-lg shadow-slate-200"
            )}
          >
            {isGlitch ? 'EJECUTAR COMPRA YA' : 'VER EN TIENDA'}
            <ExternalLink size={14} />
          </a>
        </div>
      </div>
    </div>
  );
};
