
import { NextRequest, NextResponse } from "next/server";
import { getUnifiedProducts } from "@/lib/db";

/**
 * 🤖 TELEGRAM FEED API (SIN ROSTRO)
 * Endpoint para automatización de alertas externas.
 * Criterios: ROI > 25%, Match Confirmado.
 */
export async function GET(req: NextRequest) {
    try {
        // Obtenemos un lote fresco del mercado (1000 productos)
        const products = await getUnifiedProducts(null, "", 1000);

        // Filtro estricto para Telegram: Alta Rentabilidad y Verificación Confirmada
        const deals = products
            .filter(p =>
                (p.gap_market || 0) > 30 &&
                p.confidence === "ALTA" &&
                p.market_min > p.price
            )
            .map(p => {
                const profitArs = p.market_min - p.price;
                const formattedPrice = new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS", maximumFractionDigits: 0 }).format(p.price);
                const formattedProfit = new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS", maximumFractionDigits: 0 }).format(profitArs);

                // Texto pre-formateado para el Bot
                const telegramMessage = `
🔥 *ALERTA DE ARBITRAJE* 🔥
--------------------------
📦 *${p.name}*
🏢 Tienda: ${p.store}
💰 Precio Odiseo: *${formattedPrice}*
📊 Precio Mercado: ${new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS", maximumFractionDigits: 0 }).format(p.market_min)}

🟢 *GANANCIA EST.: ${formattedProfit}*
📉 Gap: ${p.gap_market.toFixed(0)}%

🔗 [VER OFERTA AQUÍ](${p.url})
--------------------------
#${p.store.replace(/\s+/g, '')} #Oportunidad
                `.trim();

                return {
                    id: p.match_key,
                    name: p.name,
                    store: p.store,
                    price: p.price,
                    market_price: p.market_min,
                    profit_ars: profitArs,
                    gap_pct: p.gap_market,
                    url: p.url,
                    telegram_payload: telegramMessage
                };
            });

        return NextResponse.json({
            success: true,
            count: deals.length,
            timestamp: new Date().toISOString(),
            deals: deals
        });

    } catch (error) {
        return NextResponse.json({ success: false, error: "Error interno del servidor" }, { status: 500 });
    }
}
