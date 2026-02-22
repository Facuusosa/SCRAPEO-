
import sqlite3
import json
from datetime import datetime
import re

def clean_text(text):
    if not text: return ""
    # Clean up messy scraping artifacts
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def format_cat(cat):
    if not cat: return "General"
    return cat.split('/')[-1].replace('-', ' ').title()

def generate_html_report():
    db_path = "fravega_monitor.db"
    output_path = "catalogo_ofertas.html"
    
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Stats
            total_products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
            total_alerts = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
            
            # Categories
            categories_rows = conn.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL").fetchall()
            categories = sorted([row['category'] for row in categories_rows])
            
            # All products - Logic: Prioritize Alerts (Recent Price Drop) -> Then Low Price -> Then All
            products_rows = conn.execute("""
                SELECT p.*, p.image_url, a.old_price, a.new_price 
                FROM products p
                LEFT JOIN (
                    SELECT product_id, old_price, new_price
                    FROM alerts 
                    WHERE id IN (SELECT MAX(id) FROM alerts GROUP BY product_id)
                ) a ON p.id = a.product_id
                ORDER BY 
                    (a.old_price IS NOT NULL AND a.new_price < a.old_price) DESC, -- First: Real Drops
                    (p.last_price <= p.lowest_price) DESC, -- Second: Historic Lows
                    p.last_seen DESC -- Then: Freshness
            """).fetchall()

    
        # Generate Rows HTML outside f-string to allow complex logic easier.
        products_html = ""
        for row in products_rows:
            
            # Logic for Badges
            badge_html = ""
            if row['old_price'] and row['new_price'] < row['old_price']:
                drop_pct = ((row["old_price"] - row["new_price"]) / row["old_price"]) * 100
                badge_html = f'<div class="intel-badge bg-drop">BAJÓ {drop_pct:.0f}%</div>'
            elif row['last_price'] <= row['lowest_price']:
                badge_html = '<div class="intel-badge bg-margin">PRECIO TOP</div>'
            elif row['last_price'] < 5000: # Glitch suspicion
                 badge_html = '<div class="intel-badge bg-glitch">POSIBLE GLITCH</div>'

            # Logic for Image
            img_src = row['image_url'] if 'image_url' in row.keys() and row['image_url'] else 'https://via.placeholder.com/300?text=No+Image'
            
            # Logic for Brand/Seller
            brand = row['brand_name'] if 'brand_name' in row.keys() and row['brand_name'] else 'GENERIC'
            seller = clean_text(row['seller_name'] if 'seller_name' in row.keys() and row['seller_name'] else 'Fravega')
            
            # Logic for Analysis Box
            if row['old_price']:
                analysis_html = """
                <div class="analysis-box">
                    <span style="font-size:1.2rem">📉</span> <span>Detectamos una bajada de precio real en este ciclo.</span>
                </div>
                """
            else:
                 analysis_html = """
                <div class="analysis-box" style="border-color:var(--border); color:var(--text-muted); background:transparent;">
                     <span>Precio estable. Sin movimiento detectado.</span>
                </div>
                """
            
            # Logic for SKU/ID for link
            item_id = row['sku_code'] if 'sku_code' in row.keys() and row['sku_code'] else row['id']
            
            old_price_val = row['old_price'] if row['old_price'] else 0
            new_price_val = row['new_price'] if row['new_price'] else 0

            products_html += f'''
            <div class="product-card" 
                 data-s="{clean_text(row['title']).lower()} {item_id}" 
                 data-c="{row['category'] or ''}" 
                 data-p="{row['last_price']}"
                 data-o="{'1' if old_price_val and new_price_val < old_price_val else '0'}"
                 data-l="{'1' if row['last_price'] <= row['lowest_price'] else '0'}"
                 data-g="{'1' if row['last_price'] < 5000 else '0'}">
                
                {badge_html}
                
                <div class="card-img">
                    <img src="{img_src}" loading="lazy">
                </div>
                
                <div class="card-body">
                    <div class="meta-row">
                        <span class="brand-pill">{brand}</span>
                        <span>{seller}</span>
                    </div>
                    
                    <div class="product-title">{clean_text(row['title'])}</div>
                    
                    <div class="price-container">
                        <div class="price-row">
                            <div class="current-price">${row['last_price']:,.0f}</div>
                            {f'<div class="old-price">${row["old_price"]:,.0f}</div>' if row['old_price'] else ''}
                        </div>
                        
                        {analysis_html}

                        <div class="action-row">
                            <a href="https://www.fravega.com/p/{row['slug']}-{item_id}/" target="_blank" class="action-btn">
                                VER EN TIENDA ↗
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            '''

        # Generate Categories Options
        cat_options = "".join([f'<option value="{cat}">{format_cat(cat)}</option>' for cat in categories])

        # Write HTML using separate write calls to avoid f-string complexity issues
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CENTRO DE COMANDO ODISEO v4.0</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #09090b;
            --surface: #18181b;
            --border: #27272a;
            --text-main: #e4e4e7;
            --text-muted: #a1a1aa;
            --accent: #3b82f6; /* Azul Odiseo */
            --danger: #ef4444; /* Rojo Alerta */
            --success: #22c55e; /* Verde Oportunidad */
            --gold: #eab308; /* Dorado Glitch/Joya */
            --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            padding: 2rem;
            min-height: 100vh;
        }}
        
        /* HEADER TACTICO */
        .tactical-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
        }}
        .brand {{ font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 1.8rem; letter-spacing: -1.5px; display: flex; align-items: center; gap: 10px; }}
        .brand span {{ color: var(--accent); }}
        .status-pill {{ 
            background: rgba(34, 197, 94, 0.1); 
            color: var(--success); 
            padding: 5px 12px; 
            border-radius: 20px; 
            font-size: 0.75rem; 
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: 1px solid rgba(34, 197, 94, 0.2);
        }}
        .status-pill::before {{ content: ''; width: 6px; height: 6px; background: var(--success); border-radius: 50%; box-shadow: 0 0 8px var(--success); }}

        /* DASHBOARD METRICS */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}
        .metric-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: var(--card-shadow);
            position: relative;
            overflow: hidden;
        }}
        .metric-card::after {{ content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: var(--accent); opacity: 0.5; }}
        .metric-card:nth-child(2)::after {{ background: var(--gold); }}
        
        .metric-label {{ color: var(--text-muted); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.8rem; font-weight: 600; }}
        .metric-value {{ font-size: 2.5rem; font-weight: 800; color: #fff; line-height: 1; }}
        .metric-value.highlight {{ color: var(--gold); text-shadow: 0 0 20px rgba(234, 179, 8, 0.15); }}
        .metric-sub {{ font-size: 0.8rem; color: var(--text-muted); margin-top: 0.5rem; }}

        /* FILTROS INTEGRADOS */
        .controls-bar {{
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 1rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            align-items: center;
        }}
        .search-container {{ flex: 2; min-width: 250px; }}
        .filter-group {{ flex: 1; min-width: 150px; }}
        
        input, select {{
            width: 100%;
            padding: 0.8rem 1rem;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: #fff;
            outline: none;
            font-family: inherit;
            font-size: 0.9rem;
            transition: border-color 0.2s;
        }}
        input:focus, select:focus {{ border-color: var(--accent); }}
        input::placeholder {{ color: #52525b; }}

        /* SECCION DE OPORTUNIDADES (TOP PRIORITY) */
        .section-header {{ 
            display: flex; 
            align-items: center; 
            gap: 1rem; 
            margin-bottom: 1.5rem; 
        }}
        .section-title {{ 
            font-family: 'JetBrains Mono', monospace; 
            color: #fff; 
            font-size: 1.2rem; 
            font-weight: 700; 
        }}
        .section-line {{ flex: 1; height: 1px; background: var(--border); }}

        .opportunities-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 2rem;
            margin-bottom: 4rem;
        }}

        .product-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            overflow: hidden;
            transition: all 0.3s ease;
            position: relative;
            display: flex;
            flex-direction: column;
            box-shadow: var(--card-shadow);
        }}
        .product-card:hover {{ 
            border-color: var(--accent); 
            transform: translateY(-5px); 
            box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5); 
        }}
        
        /* Badges de Inteligencia */
        .intel-badge {{
            position: absolute;
            top: 12px;
            right: 12px;
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 0.7rem;
            font-weight: 800;
            text-transform: uppercase;
            z-index: 10;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            letter-spacing: 0.5px;
        }}
        .bg-glitch {{ background: var(--gold); color: #000; border: 1px solid rgba(255,255,255,0.4); }}
        .bg-drop {{ background: var(--success); color: #000; }}
        .bg-margin {{ background: var(--accent); color: #fff; }}

        .card-img {{
            height: 220px;
            width: 100%;
            background: #fff;
            padding: 25px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }}
        .card-img img {{ max-width: 100%; max-height: 100%; object-fit: contain; transition: transform 0.3s; }}
        .product-card:hover .card-img img {{ transform: scale(1.05); }}

        .card-body {{ padding: 1.5rem; flex: 1; display: flex; flex-direction: column; border-top: 1px solid var(--border); }}

        .meta-row {{ 
            display: flex; 
            justify-content: space-between; 
            font-size: 0.7rem; 
            color: var(--text-muted); 
            margin-bottom: 0.8rem; 
            text-transform: uppercase; 
            letter-spacing: 0.5px; 
            font-weight: 600;
        }}
        .brand-pill {{ background: #27272a; padding: 2px 6px; border-radius: 4px; }}
        
        .product-title {{ 
            font-size: 1rem; 
            font-weight: 600; 
            margin-bottom: 1rem; 
            line-height: 1.4; 
            color: #fff; 
            height: 3rem; /* Limit height */
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }}
        
        .price-container {{ margin-top: auto; }}
        
        .price-row {{ display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }}
        .current-price {{ font-size: 1.6rem; font-weight: 800; color: #fff; letter-spacing: -0.5px; }}
        .old-price {{ text-decoration: line-through; color: var(--text-muted); font-size: 0.9rem; }}
        
        .analysis-box {{ 
            background: rgba(59, 130, 246, 0.1); 
            border: 1px solid rgba(59, 130, 246, 0.2);
            padding: 8px 12px; 
            border-radius: 6px; 
            margin: 1rem 0;
            font-size: 0.75rem;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .action-row {{ 
            display: grid; 
            grid-template-columns: 1fr;
            gap: 10px; 
            margin-top: 5px;
        }}
        
        .action-btn {{
            display: flex;
            justify-content: center;
            align-items: center;
            background: #fff;
            color: #000;
            text-align: center;
            padding: 0.8rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 700;
            font-size: 0.85rem;
            transition: all 0.2s;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .action-btn:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(255, 255, 255, 0.2); }}
        
        /* ESTADOS DE VISIBILIDAD */
        #no-results {{ display: none; text-align: center; padding: 4rem; grid-column: 1/-1; color: var(--text-muted); font-size: 1.2rem; }}
    </style>
</head>
<body>

    <div class="tactical-header">
        <div class="brand">ODISEO<span>/MONITOR</span></div>
        <div class="status-pill">SISTEMA V4.0 ACTIVO</div>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-label">Productos Vigilados</div>
            <div class="metric-value">{total_products}</div>
            <div class="metric-sub">Base de datos en crecimiento</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Oportunidades Activas</div>
            <div class="metric-value highlight">{total_alerts}</div>
            <div class="metric-sub">Glitches o bajadas reales</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Último Barrido</div>
            <div class="metric-value" style="font-size: 2rem; color: var(--accent);">{datetime.now().strftime('%H:%M')}</div>
            <div class="metric-sub">Escaneo en tiempo real</div>
        </div>
    </div>

    <!-- BARRA DE CONTROL -->
    <div class="controls-bar">
        <div class="search-container">
            <input type="text" id="s" placeholder="🔍 Buscar producto, marca o modelo..." oninput="go()">
        </div>
        <div class="filter-group">
             <select id="c" onchange="go()">
                <option value="">📂 Todas las Categorías</option>
                {cat_options}
            </select>
        </div>
        <div class="filter-group">
            <select id="t" onchange="go()">
                <option value="all">👁️ Ver Todo</option>
                <option value="offer">🔥 Solo Ofertas Reales</option>
                <option value="low">✅ Mínimos Históricos</option>
                <option value="glitch">⚡ Posibles Glitches</option>
            </select>
        </div>
    </div>

    <!-- SECCION PRINCIPAL DE TARJETAS -->
    <div class="section-header">
        <div class="section-title">📡 RADAR DE PRODUCTOS</div>
        <div class="section-line"></div>
    </div>
    
    <div class="opportunities-grid">
        {products_html}
        
        <div id="no-results">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📡</div>
            No se encontraron señales con estos filtros.<br>
            <span style="font-size: 0.9rem; opacity: 0.7;">Intenta ampliar la búsqueda o espera al próximo barrido.</span>
        </div>
    </div>

    <script>
        function go() {{
            const s = document.getElementById('s').value.toLowerCase();
            const c = document.getElementById('c').value;
            const t = document.getElementById('t').value;
            
            const cards = document.getElementsByClassName('product-card');
            let found = 0;
            
            for (let card of cards) {{
                const matchS = !s || card.dataset.s.includes(s);
                const matchC = !c || card.dataset.c === c;
                
                let matchT = true;
                if (t === 'offer') matchT = card.dataset.o === '1';
                if (t === 'low') matchT = card.dataset.l === '1';
                if (t === 'glitch') matchT = card.dataset.g === '1';
                
                if (matchS && matchC && matchT) {{
                    card.style.display = 'flex';
                    found++;
                }} else {{
                    card.style.display = 'none';
                }}
            }}
            document.getElementById('no-results').style.display = found ? 'none' : 'block';
        }}
        // Auto-run filters on load
        go();
    </script>
</body>
</html>
""")
        print(f"✅ Dashboard Táctico actualizado.")

    except Exception as e:
        print(f"Error crítico generando dashboard: {e}")

if __name__ == "__main__":
    generate_html_report()
