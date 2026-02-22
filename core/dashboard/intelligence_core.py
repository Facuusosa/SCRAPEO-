"""
INTELLIGENCE CORE - SHARED STRATEGY
Unified data gathering and arbitrage analysis.
"""
import os
import sqlite3
import re
import time

def make_match_key(name):
    if not name: return ""
    return re.sub(r'[^a-zA-Z0-9]', '', name.lower())[:35]

def get_unified_data(limit_per_store=2500):
    all_prods = []
    cats = set()
    
    # Project Root is 2 levels up from core/dashboard/
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    DB_PATHS = {
        "Fravega": "data/databases/fravega_monitor.db",
        "OnCity": "data/databases/oncity_monitor.db",
        "Cetrogar": "data/databases/cetrogar_monitor.db",
        "Megatone": "data/databases/megatone_monitor.db",
        "Newsan": "data/databases/newsan_monitor.db",
        "CasaDelAudio": "data/databases/casadelaudio_monitor.db"
    }
    
    for store, rel_path in DB_PATHS.items():
        abs_path = os.path.join(root_dir, rel_path.replace('/', os.sep))
        if not os.path.exists(abs_path):
            print(f"[CORE] DB NOT FOUND for {store}: {abs_path}")
            continue
        
        print(f"[CORE] Loading {store} from {abs_path}")
        
        try:
            conn = sqlite3.connect(f"file:{abs_path}?mode=ro", uri=True, timeout=10)
            conn.row_factory = sqlite3.Row
            cols = [c[1] for c in conn.execute("PRAGMA table_info(products)").fetchall()]
            
            n_c = "name" if "name" in cols else "title"
            b_c = "brand" if "brand" in cols else "brand_name"
            u_c = "url" if "url" in cols else "slug"
            
            rows = conn.execute(f"SELECT * FROM products WHERE last_price > 500").fetchall()
            for r in rows:
                p = dict(r)
                price = p.get("last_price") or p.get("price") or 0
                list_price = p.get("list_price") or 0
                cat = p.get("category") or "General"
                cats.add(cat)
                
                # Extraer stock (algunos lo tienen como int, otros bool)
                stock_val = p.get("stock")
                if stock_val is None: stock_val = True # Default true if unknown
                
                all_prods.append({
                    "id": p.get("id"),
                    "name": p.get(n_c) or "Sin nombre",
                    "brand": p.get(b_c) or "GENERIC",
                    "price": price,
                    "list_price": list_price,
                    "discount": p.get("discount_pct") or 0,
                    "url": p.get(u_c) or "#",
                    "img": p.get("image_url") or "",
                    "store": store,
                    "cat": cat,
                    "stock": bool(stock_val),
                    "last_seen": p.get("last_seen") or p.get("scraped_at") or "",
                    "profit": (list_price - price) if list_price > price else 0
                })
            conn.close()
        except: pass

    # Cross-Store Arbitrage
    market_map = {}
    for p in all_prods:
        key = make_match_key(p['name'])
        if key not in market_map: market_map[key] = []
        market_map[key].append(p)

    enriched = []
    for p in all_prods:
        key = make_match_key(p['name'])
        peers = market_map.get(key, [])
        others = [o for o in peers if o['store'] != p['store']]
        
        p['others'] = [{"store": o['store'], "price": o['price']} for o in others[:3]]
        p['gap'] = 0
        if others:
            min_market = min(o['price'] for o in others)
            if p['price'] < min_market:
                p['gap'] = round(((min_market - p['price']) / min_market) * 100)
        enriched.append(p)
        
    return enriched, sorted(list(cats))

def get_all_alerts(limit=50):
    all_alerts = []
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    DB_PATHS = {
        "Fravega": "data/databases/fravega_monitor.db",
        "OnCity": "data/databases/oncity_monitor.db",
        "Cetrogar": "data/databases/cetrogar_monitor.db",
        "Megatone": "data/databases/megatone_monitor.db",
        "Newsan": "data/databases/newsan_monitor.db",
        "CasaDelAudio": "data/databases/casadelaudio_monitor.db"
    }
    
    for store, rel_path in DB_PATHS.items():
        abs_path = os.path.join(root_dir, rel_path.replace('/', os.sep))
        if not os.path.exists(abs_path):
            continue
            
        try:
            conn = sqlite3.connect(f"file:{abs_path}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            
            # Buscamos en la tabla de alertas
            query = """
                SELECT a.*, p.name, p.brand, p.image_url, p.url 
                FROM alerts a
                JOIN products p ON a.product_id = p.id
                ORDER BY a.timestamp DESC LIMIT ?
            """
            rows = conn.execute(query, (limit,)).fetchall()
            for r in rows:
                item = dict(r)
                item['store'] = store
                # Calcular drop %
                old = item.get('old_price', 0)
                new = item.get('new_price', 0)
                if old > 0:
                    item['drop_pct'] = round(((old - new) / old) * 100)
                else:
                    item['drop_pct'] = 0
                all_alerts.append(item)
            conn.close()
        except:
            pass
            
    # Ordenar todas por timestamp descendente
    all_alerts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return all_alerts[:limit]

def get_product_history(store, product_id):
    """Obtiene los últimos cambios de precio de un producto específico."""
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DB_PATHS = {
        "Fravega": "data/databases/fravega_monitor.db",
        "OnCity": "data/databases/oncity_monitor.db",
        "Cetrogar": "data/databases/cetrogar_monitor.db",
        "Megatone": "data/databases/megatone_monitor.db",
        "Newsan": "data/databases/newsan_monitor.db",
        "CasaDelAudio": "data/databases/casadelaudio_monitor.db"
    }
    
    rel_path = DB_PATHS.get(store)
    if not rel_path: return []
    
    abs_path = os.path.join(root_dir, rel_path.replace('/', os.sep))
    if not os.path.exists(abs_path): return []
    
    history = []
    try:
        conn = sqlite3.connect(f"file:{abs_path}?mode=ro", uri=True)
        query = "SELECT old_price, new_price, timestamp FROM alerts WHERE product_id = ? ORDER BY timestamp ASC"
        rows = conn.execute(query, (product_id,)).fetchall()
        for r in rows:
            history.append({
                "price": r[1],
                "date": r[2]
            })
        conn.close()
    except: pass
    return history
