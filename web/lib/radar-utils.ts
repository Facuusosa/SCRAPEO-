/**
 * Utilidades para procesar y filtrar el Radar de Oportunidades.
 */

export interface RadarFilters {
    limit?: number;
    offset?: number;
    tienda?: string;
    descuento_min?: number;
    categoria?: string;
    precio_max?: number;
}

export function applyRadarFiltros(products: any[], filters: RadarFilters) {
    let filtered = products;

    // 1. Lógica Híbrida: Gap Market > 12% O Descuento > 35%
    filtered = filtered.filter(p => (p.gap_market > 12) || (p.discount_pct > 35));

    // 2. Filtro por Tienda
    if (filters.tienda) {
        filtered = filtered.filter(p => p.store.toLowerCase() === filters.tienda?.toLowerCase());
    }

    // 3. Filtro por Descuento Mínimo Adicional
    if (filters.descuento_min) {
        filtered = filtered.filter(p => p.discount_pct >= (filters.descuento_min || 0));
    }

    // 4. Filtro por Categoría
    if (filters.categoria) {
        filtered = filtered.filter(p => p.category?.toLowerCase().includes(filters.categoria?.toLowerCase() || ""));
    }

    // 5. Filtro por Precio Máximo
    if (filters.precio_max) {
        filtered = filtered.filter(p => p.price <= (filters.precio_max || 99999999));
    }

    // 6. Ordenamiento: Prioridad a mayor Gap de Mercado
    return filtered.sort((a, b) => (b.gap_market || 0) - (a.gap_market || 0));
}
