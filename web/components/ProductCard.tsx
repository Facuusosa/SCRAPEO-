"use client";

import React, { useState, useMemo, useEffect } from "react";
import { Store, AlertTriangle, Shield, Zap, DollarSign, Bomb } from "lucide-react";
import { cn, sanitizeUrl } from "@/lib/utils";

export interface Product {
  name: string;
  price: number;
  list_price: number;
  discount_pct: number;
  brand: string;
  img: string;
  url: string;
  store: string;
  category?: string;
  market_min?: number;
  market_average?: number;
  gap_market?: number;
  competitors?: { store: string; price: number; url?: string }[];
  confidence?: string;
  stock_status?: string;
}

export const ProductCard = ({ product, isBomb = false }: { product: Product, isBomb?: boolean }) => {
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

  const marketRef = product.market_average || product.market_min || 0;
  const savingsArs = marketRef > product.price ? marketRef - product.price : 0;
  const savingsPct = marketRef > 0 ? (savingsArs / marketRef) * 100 : 0;

  // Mocked stock timer for visual effect as requested
  const [timeLeft, setTimeLeft] = useState<number>(Math.floor(Math.random() * 60) + 10);
  useEffect(() => {
    if (!isBomb) return;
    const timer = setInterval(() => {
      setTimeLeft((prev: number) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [isBomb]);

  return (
    <div className={cn(
      "group bg-white rounded-[24px] border border-slate-200 overflow-hidden transition-all duration-500 pro-shadow pro-shadow-hover flex flex-col h-full relative",
      isHighOpportunity && "border-emerald-400 ring-2 ring-emerald-50/50",
      isSuspect && "border-amber-300 ring-2 ring-amber-50",
      isBomb && "border-red-500 ring-4 ring-red-500/20 bg-slate-950 text-white"
    )}>
      {isBomb && (
        <div className="absolute inset-0 border-[2px] border-red-500/50 pointer-events-none animate-pulse rounded-[24px] z-50 shadow-[0_0_20px_rgba(239,68,68,0.3)]"></div>
      )}

      {/* Media Section */}
      <div className={cn(
        "relative aspect-square p-4 flex items-center justify-center overflow-hidden border-b",
        isBomb ? "bg-slate-900 border-slate-800" : "bg-white border-slate-50"
      )}>
        <img
          src={product.img || "/placeholder.png"}
          alt={product.name}
          className="max-h-full max-w-full object-contain transition-transform duration-700 group-hover:scale-105"
          onError={(e: React.SyntheticEvent<HTMLImageElement, Event>) => (e.currentTarget.src = "https://placehold.co/400x300?text=Sin+Imagen")}
        />

        <div className="absolute top-3 left-3 z-10">
          <div className={cn(
            "px-2.5 py-1 rounded-lg flex items-center gap-1.5 shadow-xl border",
            isBomb ? "bg-red-600 border-red-400 text-white" : "bg-slate-900/95 border-white/20 text-white"
          )}>
            <Store size={9} className={isBomb ? "text-white" : "text-blue-400"} />
            <span className="text-[9px] font-black uppercase tracking-tighter">{product.store}</span>
          </div>
        </div>

        {isBomb && (
          <div className="absolute top-3 right-3 z-10">
            <div className="bg-slate-950/80 backdrop-blur-md border border-red-500/50 text-red-500 px-2 py-1 rounded-md flex items-center gap-1.5">
              <Zap size={10} fill="currentColor" />
              <span className="text-[10px] font-mono font-black tabular-nums">00:{timeLeft.toString().padStart(2, '0')}</span>
            </div>
          </div>
        )}

        {isHighOpportunity && !isBomb && (
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
            <span className={cn(
              "text-[9px] font-black uppercase tracking-tighter px-2.5 py-1 rounded-md border",
              isBomb ? "bg-red-500/20 border-red-500/30 text-red-400" : "bg-blue-50 border-blue-100/50 text-blue-600"
            )}>
              {product.brand || "E-Commerce"}
            </span>
            <div className="flex items-center gap-1.5">
              {(product.confidence === "ALTA" || isBomb) && <Shield size={10} className="text-emerald-500 fill-emerald-50" />}
              <span className={cn(
                "text-[8px] font-black uppercase tracking-widest",
                isBomb ? "text-slate-400" : "text-slate-400"
              )}>
                {product.confidence === "ALTA" || isBomb ? "VERIFICADO" : "MUESTREO"}
              </span>
            </div>
          </div>
          <h3 className={cn(
            "text-sm font-black line-clamp-2 leading-tight min-h-[2.5rem] tracking-tight transition-colors",
            isBomb ? "text-white group-hover:text-red-400" : "text-slate-900 group-hover:text-blue-600"
          )}>
            {product.name}
          </h3>
        </div>

        {/* Intelligence Table - Radar Arbitraje Style */}
        <div className={cn(
          "rounded-[20px] border mb-4 p-3.5 transition-all duration-300",
          isBomb ? "bg-slate-900 border-slate-800" : (isSuspect ? "bg-amber-50 border-amber-200" : "bg-slate-50 border-slate-100 group-hover:bg-blue-50/50 group-hover:border-blue-100")
        )}>
          <div className="flex justify-between items-center text-[8px] font-black uppercase tracking-widest mb-2.5 px-0.5 text-slate-400">
            <span>PROMEDIO MERCADO</span>
            <span>GAÍN RADAR</span>
          </div>
          <div className="flex items-center justify-between mb-3">
            <span className={cn(
              "text-base font-black font-mono tracking-tighter tabular-nums",
              isBomb ? "text-slate-300" : "text-slate-900"
            )}>{formatPrice(marketRef)}</span>
            <div className="flex flex-col items-end">
              <span className={cn(
                "text-[11px] font-black font-mono px-2.5 py-1 rounded-full shadow-sm tabular-nums",
                isBomb ? "bg-red-600 text-white animate-pulse" : (isHighOpportunity ? "bg-emerald-500 text-white animate-pulse" : "bg-slate-200 text-slate-600")
              )}>
                {savingsPct > 0 ? `-${savingsPct.toFixed(0)}%` : '--'}
              </span>
            </div>
          </div>

          {/* Ahorro Comparativo */}
          <div className={cn(
            "mt-2 pt-2.5 border-t space-y-1.5",
            isBomb ? "border-slate-800" : "border-slate-200/60"
          )}>
            <div className="flex justify-between items-center">
              <span className="text-[9px] font-bold text-slate-500 uppercase tracking-tighter">AHORRO NETO</span>
              <span className={cn(
                "text-xs font-black font-mono tracking-tighter tabular-nums",
                isBomb ? "text-red-400" : "text-emerald-600"
              )}>{formatPrice(savingsArs)}</span>
            </div>
          </div>
        </div>

        {/* Pricing & CTA */}
        <div className="mt-auto pt-2">
          <div className="flex flex-col mb-4">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[8px] font-black text-slate-400 uppercase tracking-widest">PRECIO ODISEO</span>
              <span className={cn(
                "text-[8px] font-bold px-2 py-0.5 rounded-full",
                isBomb ? "bg-red-500/20 text-red-500" : "bg-emerald-50 text-emerald-600"
              )}>STOCK CRÍTICO</span>
            </div>
            <span className={cn(
              "text-2xl font-black tracking-tighter leading-none font-mono tabular-nums",
              isBomb ? "text-white" : "text-slate-900"
            )}>
              {formatPrice(product.price)}
            </span>
          </div>

          <a
            href={sanitizeUrl(product.url, product.store)}
            target="_blank"
            rel="noopener noreferrer"
            className={cn(
              "w-full py-2.5 rounded-lg text-[8px] font-black uppercase tracking-widest flex items-center justify-center gap-2 shadow-lg transition-all active:scale-95",
              isBomb ? "bg-red-600 text-white hover:bg-red-700 shadow-red-500/20" : "bg-slate-900 text-white hover:bg-slate-800"
            )}
          >
            🎯 EJECUTAR COMPRA
          </a>
        </div>
      </div>
    </div>
  );
};
