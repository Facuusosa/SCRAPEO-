"""
🔍 SUPER BUSCADOR — El Oráculo de los Precios Bajos
Busca en todas las bases de datos locales al mismo tiempo.
"""
import os
import sqlite3
import sys
from datetime import datetime

# Resolver paths absolutos para las DBs
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Resolver paths absolutos para las DBs
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(ROOT_DIR, "data", "databases")

DB_FILES = {
    "Fravega": os.path.join(DB_DIR, "fravega_monitor.db"),
    "OnCity": os.path.join(DB_DIR, "oncity_monitor.db"),
    "Cetrogar": os.path.join(DB_DIR, "cetrogar_monitor.db"),
    "Megatone": os.path.join(DB_DIR, "megatone_monitor.db"),
    "Newsan": os.path.join(DB_DIR, "newsan_monitor.db"),
    "CasaDelAudio": os.path.join(DB_DIR, "casadelaudio_monitor.db")
}

def buscar(query):
    query_clean = query.lower().strip()
    all_results = []

    print(f"\n🔎 Buscando '{query}' en todo el mercado...")
    print("-" * 80)

    for name, db_path in DB_FILES.items():
        if not os.path.exists(db_path):
            continue
            
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            
            # Handle schema differences
            name_col = "title" if name == "Fravega" else "name"
            brand_col = "brand_name" if name == "Fravega" else "brand"
            url_col = "slug" if name == "Fravega" else "url"
            
            # Buscar productos que coincidan
            query_sql = f"""
                SELECT {name_col} as name, {brand_col} as brand, last_price, list_price, 
                       (CASE WHEN list_price > last_price THEN ((list_price - last_price)/list_price)*100 ELSE 0 END) as discount_pct,
                       {url_col} as url
                FROM products 
                WHERE {name_col} LIKE ?
                ORDER BY last_price ASC
            """
            
            rows = conn.execute(query_sql, (f'%{query_clean}%',)).fetchall()
            
            for r in rows:
                all_results.append({
                    'tienda': name,
                    'nombre': r['name'],
                    'precio': r['last_price'],
                    'lista': r['list_price'],
                    'descuento': r['discount_pct'],
                    'url': r['url']
                })
            conn.close()
        except Exception as e:
            print(f"⚠️ Error en {name}: {e}")

    # Ordenar todos por precio ascendente
    all_results.sort(key=lambda x: x['precio'])

    if not all_results:
        print("❌ No se encontraron resultados con ese nombre.")
        return

    print(f"{'PRECIO':12s} | {'TIENDA':12s} | {'PRODUCTO'}")
    print("-" * 80)
    for p in all_results[:20]: # Top 20 resultados
        # Formatear precio con color si es barato? (basico por ahora)
        precio_str = f"${p['precio']:,.0f}"
        print(f"{precio_str:12s} | {p['tienda']:12s} | {p['nombre'][:60]}")
    
    # Mostrar la mejor opcion
    best = all_results[0]
    print("-" * 80)
    print(f"⭐ MEJOR PRECIO: ${best['precio']:,.0f} en {best['tienda']}")
    print(f"🔗 Link: {best['url']}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        buscar(" ".join(sys.argv[1:]))
    else:
        print("Uso: python super_buscador.py [termino de busqueda]")
