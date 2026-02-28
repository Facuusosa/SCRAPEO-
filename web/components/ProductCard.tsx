"use client";

import React, { useState, useMemo, useEffect } from "react";
import { Store, AlertTriangle, Shield, Zap, DollarSign, Bomb } from "lucide-react";
import { cn, sanitizeUrl } from "@/lib/utils";

interface Product {
  name: string;
  price: number;
  list_price: number;
  discount_pct: number;
  brand: string;
  img: string;
  url: string;
  store: string;
  market_min?: number;
  gap_market?: number;
  competitors?: { store: string; price: number; url?: string }[];
  confidence?: string;
}

export const ProductCard = ({ product }: { product: Product }) => {
  const formatPrice = (p: number) => {
    return new Intl.NumberFormat("es-AR", {
      style: "currency",
      currency: "ARS",
      maximumFractionDigits: 0,
    }).format(p || 0);
  };

  const gap = product.gap_market || 0;
  const isHighOpportunity = gap > 15 && gap <= 100;
  const isSuspect = gap > 100;

  const marketRef = product.market_min || 0;
  const profitArs = marketRef > product.price ? marketRef - product.price : 0;
  const bestCompetitor = product.competitors?.sort((a, b) => a.price - b.price)[0];

  return (
    <div className={cn(
      "group bg-white rounded-[24px] border border-slate-200 overflow-hidden transition-all duration-500 pro-shadow pro-shadow-hover flex flex-col h-full",
      isHighOpportunity && "border-emerald-400 ring-2 ring-emerald-50/50",
      isSuspect && "border-amber-300 ring-2 ring-amber-50"
    )}>
      {/* Media Section */}
      <div className="relative aspect-square bg-white p-4 flex items-center justify-center overflow-hidden border-b border-slate-50">
        <img
          src={product.img || "/placeholder.png"}
          alt={product.name}
          className="max-h-full max-w-full object-contain transition-transform duration-700 group-hover:scale-105"
          onError={(e) => (e.currentTarget.src = "https://placehold.co/400x300?text=Sin+Imagen")}
        />

        <div className="absolute top-3 left-3 z-10">
          <div className="bg-slate-900/95 backdrop-blur-md text-white px-2.5 py-1 rounded-lg flex items-center gap-1.5 shadow-xl border border-white/20">
            <Store size={9} className="text-blue-400" />
            <span className="text-[9px] font-black uppercase tracking-tighter">{product.store}</span>
          </div>
        </div>

        {isHighOpportunity && (
          <div className="absolute -top-1 -right-1 z-20">
            <div className="bg-red-600 text-white text-[8px] font-black uppercase px-2.5 py-1.5 rounded-bl-2xl rounded-tr-[24px] shadow-lg flex items-center gap-1 border-b border-l border-red-400/50 animate-in">
              <Bomb size={10} fill="white" className="animate-pulse" /> BOMBA
            </div>
          </div>
        )}
      </div>

      {/* Content Section */}
      <div className="p-4 flex flex-col flex-1">
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[9px] font-black text-blue-600 uppercase tracking-tighter bg-blue-50 px-2.5 py-1 rounded-md border border-blue-100/50">
              {product.brand || "E-Commerce"}
            </span>
            <div className="flex items-center gap-1.5">
              {product.confidence === "ALTA" && <Shield size={10} className="text-emerald-500 fill-emerald-50" />}
              <span className="text-[8px] font-black text-slate-400 uppercase tracking-widest">
                {product.confidence === "ALTA" ? "VERIFICADO" : "MUESTREO"}
              </span>
            </div>
          </div>
          <h3 className="text-sm font-black text-slate-900 line-clamp-2 leading-tight min-h-[2.5rem] tracking-tight group-hover:text-blue-600 transition-colors">
            {product.name}
          </h3>
        </div>

        {/* Intelligence Table - High Density */}
        <div className={cn(
          "rounded-[20px] border mb-4 p-3.5 transition-all duration-300",
          isSuspect ? "bg-amber-50 border-amber-200" : "bg-slate-50 border-slate-100 group-hover:bg-blue-50/50 group-hover:border-blue-100"
        )}>
          <div className="flex justify-between items-center text-[8px] font-black text-slate-400 uppercase tracking-widest mb-2.5 px-0.5">
            <span>Mercado</span>
            <span>Ahorro</span>
          </div>
          <div className="flex items-center justify-between mb-3">
            <span className="text-base font-black text-slate-900 font-mono tracking-tighter tabular-nums">{formatPrice(marketRef)}</span>
            <span className={cn(
              "text-[11px] font-black font-mono px-2.5 py-1 rounded-full shadow-sm tabular-nums",
              isHighOpportunity ? "bg-emerald-500 text-white animate-pulse" : "bg-slate-200 text-slate-600"
            )}>
              {gap > 0 ? `+${gap.toFixed(0)}%` : '--'}
            </span>
          </div>

          {/* Comparativa Directa */}
          {product.competitors && product.competitors.length > 0 && (
            <div className="mt-2 pt-2.5 border-t border-slate-200/60 space-y-1.5">
              {product.competitors.slice(0, 2).map((comp, idx) => (
                <div key={idx} className="flex justify-between items-center opacity-70 group-hover:opacity-100 transition-opacity">
                  <span className="text-[9px] font-bold text-slate-500">{comp.store}</span>
                  <span className="text-[9px] font-black text-slate-600 font-mono line-through tracking-tighter tabular-nums">{formatPrice(comp.price)}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Pricing & CTA */}
        <div className="mt-auto pt-2">
          <div className="flex flex-col mb-4">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[8px] font-black text-slate-400 uppercase tracking-widest">Precio Hoy</span>
              <span className="text-[8px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">Sincronizado</span>
            </div>
            <span className="text-2xl font-black text-slate-900 tracking-tighter leading-none font-mono tabular-nums">
              {formatPrice(product.price)}
            </span>
          </div>

          <a
            href={sanitizeUrl(product.url, product.store)}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full py-2.5 rounded-lg bg-slate-900 text-white text-[8px] font-black uppercase tracking-widest flex items-center justify-center gap-2 shadow-lg hover:bg-slate-800 transition-all active:scale-95"
          >
            🛒 Ver Oferta
          </a>
        </div>
      </div>
    </div>
  );
};
