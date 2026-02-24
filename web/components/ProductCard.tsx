"use client";

import React, { useState } from "react";
import { Store, AlertTriangle, Shield, Zap, DollarSign } from "lucide-react";
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
      "group bg-white rounded-[32px] border border-slate-200 overflow-hidden transition-all duration-500 pro-shadow pro-shadow-hover flex flex-col h-full",
      isHighOpportunity && "border-emerald-400 ring-4 ring-emerald-50/50",
      isSuspect && "border-amber-300 ring-4 ring-amber-50"
    )}>
      {/* Media Section */}
      <div className="relative aspect-square bg-white p-6 flex items-center justify-center overflow-hidden border-b border-slate-100">
        <img
          src={product.img || "/placeholder.png"}
          alt={product.name}
          className="max-h-full max-w-full object-contain transition-transform duration-700 group-hover:scale-110"
          onError={(e) => (e.currentTarget.src = "https://placehold.co/400x300?text=Sin+Imagen")}
        />

        {/* Badge de Diferencia (Impacto Inmediato) */}
        {profitArs > 5000 && !isSuspect && (
          <div className="absolute bottom-4 left-4 right-4 translate-y-2 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300 z-10">
            <div className="bg-emerald-500 text-white py-3 px-4 rounded-2xl shadow-xl shadow-emerald-200 flex items-center justify-center gap-2">
              <DollarSign size={16} strokeWidth={3} />
              <span className="text-sm font-black uppercase tracking-tighter">Margen a favor: {formatPrice(profitArs)}</span>
            </div>
          </div>
        )}

        <div className="absolute top-4 left-4">
          <div className="bg-slate-900 text-white px-3 py-1.5 rounded-full flex items-center gap-2 shadow-xl border border-white/10">
            <Store size={10} />
            <span className="text-[9px] font-black uppercase tracking-widest">{product.store}</span>
          </div>
        </div>

        {isHighOpportunity && (
          <div className="absolute top-4 right-4">
            <div className="bg-emerald-600 text-white text-[9px] font-black uppercase px-3 py-1.5 rounded-full shadow-xl flex items-center gap-2">
              <Zap size={10} fill="white" /> OPORTUNIDAD CONFIRMADA
            </div>
          </div>
        )}

        {isSuspect && (
          <div className="absolute top-4 right-4">
            <div className="bg-amber-500 text-white text-[9px] font-black uppercase px-3 py-1.5 rounded-full shadow-xl flex items-center gap-2">
              <AlertTriangle size={10} /> VALIDAR MODELO
            </div>
          </div>
        )}
      </div>

      {/* Content Section */}
      <div className="p-6 flex flex-col flex-1">
        {/* Fila de Diferencia (Siempre Visible) */}
        {profitArs > 0 && !isSuspect && (
          <div className="mb-4 bg-emerald-50 border border-emerald-100 py-2 px-4 rounded-xl flex items-center justify-between">
            <span className="text-[9px] font-black text-emerald-600 uppercase tracking-widest">Diferencia vs Mercado</span>
            <span className="text-sm font-black text-emerald-600">+{formatPrice(profitArs)}</span>
          </div>
        )}

        <div className="mb-4">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[9px] font-black text-slate-400 uppercase tracking-[0.2em]">{product.brand || "E-Commerce"}</span>
            <div className="flex items-center gap-1.5">
              {product.confidence === "ALTA" && <Shield size={12} className="text-blue-500" />}
              <span className="text-[9px] font-black text-slate-500 uppercase">{product.confidence === "ALTA" ? "PRECITO ALTO" : "MUESTREO"}</span>
            </div>
          </div>
          <h3 className="text-base font-bold text-slate-900 line-clamp-2 leading-snug min-h-[2.8rem]">
            {product.name}
          </h3>
        </div>

        {/* Intelligence Table */}
        <div className={cn(
          "rounded-2xl border mb-6 p-4",
          isSuspect ? "bg-amber-50 border-amber-100" : "bg-slate-50 border-slate-100"
        )}>
          <div className="flex justify-between items-center text-[9px] font-black text-slate-400 uppercase tracking-widest mb-2 px-1">
            <span>Mercado</span>
            <span>Brecha</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-bold text-slate-700">{formatPrice(marketRef)}</span>
            <div className="h-4 w-px bg-slate-200" />
            <span className={cn("text-sm font-black", isHighOpportunity ? "text-emerald-600" : "text-slate-500")}>
              {gap > 0 ? `+${gap.toFixed(0)}%` : '--'}
            </span>
          </div>
        </div>

        {/* Pricing & CTA */}
        <div className="mt-auto space-y-3">
          <div className="flex items-end justify-between">
            <div className="flex flex-col">
              <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1">Precio Compra</span>
              <span className="text-2xl font-black text-slate-900 tracking-tighter leading-none">
                {formatPrice(product.price)}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 pt-2">
            <a
              href={sanitizeUrl(product.url, product.store)}
              target="_blank"
              rel="noopener noreferrer"
              className="py-3.5 rounded-xl bg-slate-900 text-white text-[9px] font-black uppercase tracking-widest flex items-center justify-center gap-2 shadow-lg hover:bg-slate-800 transition-all active:scale-95"
            >
              🛒 Comprar
            </a>
            <a
              href={bestCompetitor ? sanitizeUrl(bestCompetitor.url || "", bestCompetitor.store) : "#"}
              target="_blank"
              rel="noopener noreferrer"
              className={cn(
                "py-3.5 rounded-xl text-[9px] font-black uppercase tracking-widest flex items-center justify-center gap-2 border transition-all active:scale-95",
                bestCompetitor
                  ? "bg-white text-slate-600 border-slate-200 hover:border-slate-900 hover:text-slate-900"
                  : "bg-slate-50 text-slate-300 border-slate-100 cursor-not-allowed pointer-events-none"
              )}
            >
              🔍 Comparar
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
