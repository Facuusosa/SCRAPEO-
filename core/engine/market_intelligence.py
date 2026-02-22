"""
📊 MARKET INTELLIGENCE — El Cerebro de los Datos
Analiza todas las bases de datos para encontrar oro real.
"""
import sqlite3
import os
import pandas as pd
from datetime import datetime

# Definir rutas a las bases de datos
DB_PATHS = {
    "Fravega": "targets/fravega/fravega_monitor.db",
    "OnCity": "oncity_monitor.db",
    "Cetrogar": "cetrogar_monitor.db",
    "Megatone": "megatone_monitor.db",
    "Newsan": "newsan_monitor.db",
    "CasaDelAudio": "casadelaudio_monitor.db"
}

def get_db_stats():
    stats = []
    for name, path in DB_PATHS.items():
        if not os.path.exists(path):
            continue
            
        try:
            conn = sqlite3.connect(path)
            # Ver si es tabla 'products' o 'items' (Fravega usa a veces distinta estructura)
            res = conn.execute("SELECT COUNT(*) FROM products").fetchone()
            count = res[0]
            
            # Ver descuento maximo
            res_disc = conn.execute("SELECT MAX(discount_pct) FROM products").fetchone()
            max_disc = res_disc[0] if res_disc[0] else 0
            
            stats.append({"Tienda": name, "Productos": count, "Max Descuento %": f"{max_disc:.1f}%"})
            conn.close()
        except Exception as e:
            stats.append({"Tienda": name, "Productos": "ERR", "Max Descuento %": "N/A"})
    
    return pd.DataFrame(stats)

def find_best_deals():
    all_deals = []
    for name, path in DB_PATHS.items():
        if not os.path.exists(path): continue
        try:
            conn = sqlite3.connect(path)
            conn.row_factory = sqlite3.Row
            
            # Handle schema differences
            name_col = "title" if name == "Fravega" else "name"
            brand_col = "brand_name" if name == "Fravega" else "brand"
            discount_col = "((list_price - last_price) / list_price * 100)" if name == "Fravega" else "discount_pct"
            url_col = "slug" if name == "Fravega" else "url"
            
            query = f"""
                SELECT {name_col} as name, {brand_col} as brand, last_price, list_price, {discount_col} as discount_pct, {url_col} as url 
                FROM products 
                WHERE last_price > 50000
                ORDER BY discount_pct DESC LIMIT 10
            """
            rows = conn.execute(query).fetchall()
            for r in rows:
                all_deals.append({
                    "Tienda": name,
                    "Producto": r["name"][:60] if r["name"] else "Sin nombre",
                    "Precio": r["last_price"],
                    "Lista": r["list_price"],
                    "Descuento": f"{r['discount_pct']:.1f}%" if r['discount_pct'] else "0%",
                    "Ahorro": (r["list_price"] or 0) - (r["last_price"] or 0)
                })
            conn.close()
        except Exception as e:
            print(f"Error in {name}: {e}")
    
    df = pd.DataFrame(all_deals)
    if not df.empty:
        return df.sort_values("Descuento", ascending=False).head(20)
    return df

def find_arbitrage():
    """
    Busca el mismo producto en distintas tiendas con precios distintos.
    Usa una búsqueda simplificada por nombre.
    """
    all_prods = []
    for name, path in DB_PATHS.items():
        if not os.path.exists(path): continue
        try:
            conn = sqlite3.connect(path)
            conn.row_factory = sqlite3.Row
            
            name_col = "title" if name == "Fravega" else "name"
            
            rows = conn.execute(f"SELECT {name_col} as name, last_price FROM products WHERE last_price > 100000").fetchall()
            for r in rows:
                if r["name"]:
                    all_prods.append({"name": r["name"].lower().strip(), "price": r["last_price"], "store": name})
            conn.close()
        except: pass
    
    if not all_prods: return "No hay datos suficientes para arbitraje."
    
    df = pd.DataFrame(all_prods)
    # Agrupar por nombre exacto (esto es difícil por las variaciones, pero probamos)
    # Filtrar solo nombres que aparecen en más de una tienda
    counts = df.groupby("name").size()
    duplicates = counts[counts > 1].index
    
    arbitrage_opportunities = []
    for name_prod in duplicates:
        items = df[df["name"] == name_prod]
        min_p = items["price"].min()
        max_p = items["price"].max()
        if max_p > min_p * 1.05: # Si hay más de 5% de diferencia
            stores = items.sort_values("price")
            cheapest = stores.iloc[0]
            expensive = stores.iloc[-1]
            arbitrage_opportunities.append({
                "Producto": name_prod[:70],
                "Min": f"${min_p:,.0f} ({cheapest['store']})",
                "Max": f"${max_p:,.0f} ({expensive['store']})",
                "Dif $": f"${(max_p - min_p):,.0f}",
                "Brecha %": f"{((max_p/min_p)-1)*100:.1f}%"
            })
            
    return pd.DataFrame(arbitrage_opportunities).sort_values("Brecha %", ascending=False).head(15)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧠 REPORTE DE INTELIGENCIA DE MERCADO")
    print("="*60)
    
    print("\n📈 ESTADO DE LAS BASES DE DATOS:")
    print(get_db_stats().to_string(index=False))
    
    print("\n🔥 TOP 20 MEJORES DESCUENTOS ENCONTRADOS:")
    deals = find_best_deals()
    if not deals.empty:
        print(deals[["Tienda", "Producto", "Precio", "Descuento", "Ahorro"]].to_string(index=False))
    else:
        print("No se encontraron descuentos significativos aún.")
        
    print("\n💰 OPORTUNIDADES DE ARBITRAJE (Diferencia de precio entre tiendas):")
    arb = find_arbitrage()
    if isinstance(arb, pd.DataFrame) and not arb.empty:
        print(arb.to_string(index=False))
    else:
        print(arb)
    
    print("\n" + "="*60)
