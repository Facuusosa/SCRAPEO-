"use client";

import React from "react";
import { ExternalLink, Tag, Store } from "lucide-react";

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
}

export const ProductCard = ({ product }: { product: Product }) => {
  const formatPrice = (p: number) => {
    return new Intl.NumberFormat("es-AR", {
      style: "currency",
      currency: "ARS",
      maximumFractionDigits: 0,
    }).format(p);
  };

  const discount = Math.round(product.discount_pct || 0);
  const isCheapest = !product.market_min || product.price <= product.market_min;

  return (
    <div className={`product-card flex flex-col h-full bg-white p-4 ${isCheapest && product.competitors?.length ? 'ring-2 ring-green-500 ring-offset-2' : ''}`}>
      {/* Etiqueta de tienda y categoría */}
      <div className="flex justify-between items-center mb-3">
        <div className="flex items-center gap-1.5 text-[11px] font-bold text-slate-500 uppercase">
          <Store size={12} />
          {product.store}
        </div>
        <div className="flex gap-2">
          {isCheapest && product.competitors?.length && (
            <span className="bg-green-100 text-green-700 text-[9px] px-2 py-0.5 rounded font-black uppercase">¡El más barato!</span>
          )}
          {discount > 0 && (
            <span className="badge-discount">-{discount}% OFF</span>
          )}
        </div>
      </div>

      {/* Imagen del Producto */}
      <div className="relative aspect-square w-full mb-4 bg-slate-50 rounded-lg flex items-center justify-center p-4 overflow-hidden">
        <img
          src={product.img || "/placeholder.png"}
          alt={product.name}
          className="max-h-full max-w-full object-contain mix-blend-multiply"
          onError={(e) => (e.currentTarget.src = "https://placehold.co/200?text=Sin+Imagen")}
        />
      </div>

      {/* Info del Producto */}
      <div className="flex flex-col flex-grow">
        <span className="text-[10px] text-blue-600 font-bold uppercase tracking-wider mb-1">
          {product.brand || "Genérico"}
        </span>
        <h3 className="text-sm font-semibold text-slate-800 line-clamp-2 mb-2 h-10 leading-tight">
          {product.name}
        </h3>

        {/* Comparativa de Mercado */}
        {product.competitors && product.competitors.length > 0 && (
          <div className="mb-4 p-2 bg-slate-50 rounded-lg border border-slate-100">
            <p className="text-[9px] font-bold text-slate-400 uppercase mb-1">Precios en otras tiendas:</p>
            {product.competitors.map((comp, i) => (
              <div key={i} className="flex justify-between text-[10px] py-0.5 border-b border-slate-100 last:border-0">
                <span className="text-slate-600 font-medium">{comp.store}</span>
                <span className={`font-bold ${comp.price > product.price ? 'text-green-600' : 'text-slate-800'}`}>
                  {formatPrice(comp.price)}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Precios */}
        <div className="mt-auto pt-2 border-t border-slate-100">
          {product.list_price > product.price && (
            <div className="price-old">{formatPrice(product.list_price)}</div>
          )}
          <div className="flex items-baseline gap-2">
            <span className="price-main">{formatPrice(product.price)}</span>
          </div>
        </div>
      </div>

      {/* Botón de Acción */}
      <a
        href={product.url}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-4 flex items-center justify-center gap-2 w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-lg transition-colors"
      >
        Ver en tienda <ExternalLink size={14} />
      </a>
    </div>
  );
};
