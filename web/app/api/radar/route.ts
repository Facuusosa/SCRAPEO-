import { NextRequest, NextResponse } from "next/server";
export const dynamic = "force-dynamic";
import { getUnifiedProducts } from "@/lib/db";
import { applyRadarFiltros, RadarFilters } from "@/lib/radar-utils";

export async function GET(req: NextRequest) {
    try {
        const { searchParams } = new URL(req.url);

        const filters: RadarFilters = {
            limit: parseInt(searchParams.get("limit") || "50"),
            offset: parseInt(searchParams.get("offset") || "0"),
            tienda: searchParams.get("tienda") || undefined,
            descuento_min: searchParams.get("descuento_min") ? parseFloat(searchParams.get("descuento_min")!) : undefined,
            categoria: searchParams.get("categoria") || undefined,
            precio_max: searchParams.get("precio_max") ? parseFloat(searchParams.get("precio_max")!) : undefined,
        };

        if (isNaN(filters.limit!) || isNaN(filters.offset!)) {
            return NextResponse.json({ success: false, error: "Parámetros numéricos inválidos" }, { status: 400 });
        }

        // 1. Obtener catálogo ampliado (traemos 5000 para filtrar con lógica híbrida en memoria)
        const allProducts = await getUnifiedProducts(null, "", 5000);

        // 2. Aplicar lógica híbrida y filtros
        const filteredProducts = applyRadarFiltros(allProducts, filters);

        // 3. Paginación final
        const paginatedItems = filteredProducts.slice(filters.offset, (filters.offset || 0) + (filters.limit || 50));

        return NextResponse.json({
            success: true,
            total: filteredProducts.length,
            limit: filters.limit,
            offset: filters.offset,
            count: paginatedItems.length,
            items: paginatedItems
        });

    } catch (error: any) {
        console.error("Error en API Radar:", error);
        return NextResponse.json({
            success: false,
            error: "Error interno del servidor",
            details: error.message
        }, { status: 500 });
    }
}
