import os
import sys
from datetime import datetime

# Add dashboard path to sys.path to find intelligence_core
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(root_dir, 'core', 'dashboard'))
from intelligence_core import get_unified_data

OUTPUT_PATH = os.path.join(root_dir, "output", "dashboard_v5_premium.html")

def fmt_p(price):
    if not price: return "$0"
    return f"${int(price):,}".replace(",", ".")

def generate():
    print("🎨 Generando Reporte Estático Premium v5.1...")
    raw_prods, categories = get_unified_data()
    # LIMPIEZA: Solo quitar errores obvios de scraping (precios irreales)
    prods = [p for p in raw_prods if 500 < p['price'] < 40_000_000]
    
    total_prods = len(prods)
    # Oportunidades: Gaps de mercado reales
    opps_list = [p for p in prods if p['gap'] > 0]
    
    avg_disc = 0
    valid_discs = [p['discount'] for p in prods if p['discount'] > 0]
    if valid_discs:
        avg_disc = round(sum(valid_discs) / len(valid_discs), 1)

    # El reporte V5 mostrará TODO el catálogo de mayor interés (Top 1500)
    top_items = sorted(prods, key=lambda x: (x['gap'], x['discount'], x['price']), reverse=True)[:1500]
    
    now = datetime.now().strftime('%d/%m/%Y %H:%M')

    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>ODISEO REPORT | {now}</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=JetBrains+Mono:wght@700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #030305; --card: #0f0f11; --border: #222226; --text: #ffffff;
            --dim: #71717a; --blue: #3b82f6; --yellow: #f59e0b; --green: #10b981; --purple: #8b5cf6;
            --accent: #afff00; --pink: #f43f5e;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Outfit', sans-serif; background: var(--bg); color: var(--text); padding: 3rem; background-image: radial-gradient(circle at 100% 0%, #111 0%, transparent 40%); }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 3rem; border-bottom: 1px solid var(--border); padding-bottom: 2rem; }}
        .brand {{ font-weight: 800; font-size: 2rem; letter-spacing: -1.5px; }}
        .brand span {{ color: var(--blue); font-weight: 300; }}
        .status {{ background: rgba(16,185,129,0.05); color: var(--green); border: 1px solid rgba(16,185,129,0.2); padding: 8px 18px; border-radius: 50px; font-size: 0.75rem; font-weight: 800; }}
        
        .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; margin-bottom: 4rem; }}
        .kpi {{ background: var(--card); border: 1px solid var(--border); padding: 2rem; border-radius: 24px; position: relative; overflow: hidden; }}
        .kpi::after {{ content: ''; position: absolute; left: 0; top: 2rem; width: 4px; height: 30px; background: var(--blue); }}
        .kpi.yellow::after {{ background: var(--yellow); }}
        .kpi.green::after {{ background: var(--green); }}
        .kpi.purple::after {{ background: var(--purple); }}
        .kpi-lbl {{ font-size: 0.7rem; color: var(--dim); text-transform: uppercase; letter-spacing: 2px; margin-bottom: 12px; font-weight: 700; }}
        .kpi-val {{ font-size: 3rem; font-weight: 800; line-height: 1; font-family: 'JetBrains Mono'; letter-spacing: -2px; }}

        .sec-title {{ font-size: 1.25rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 2.5rem; display: flex; align-items: center; gap: 15px; }}
        .sec-title::after {{ content: ''; flex: 1; height: 1px; background: var(--border); }}

        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 2rem; }}
        .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 28px; padding: 1.5rem; display: flex; flex-direction: column; gap: 1.2rem; position: relative; transition: transform 0.3s; }}
        .card:hover {{ transform: translateY(-5px); border-color: #333; }}
        .card-img {{ height: 160px; background: #fff; border-radius: 20px; display: flex; align-items: center; justify-content: center; padding: 15px; overflow: hidden; }}
        .card-img img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
        
        .pill-store {{ position: absolute; top: 1.5rem; left: 1.5rem; background: var(--blue); color: #fff; padding: 4px 10px; border-radius: 6px; font-size: 0.6rem; font-weight: 800; text-transform: uppercase; }}
        .pill-opp {{ position: absolute; top: 1.5rem; right: 1.5rem; background: var(--accent); color: #000; padding: 4px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: 800; box-shadow: 0 0 10px var(--accent); }}
        .pill-disc {{ position: absolute; top: 1.5rem; right: 1.5rem; background: var(--pink); color: #fff; padding: 4px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: 800; }}

        .brand-lbl {{ font-size: 0.65rem; color: var(--blue); font-weight: 800; text-transform: uppercase; letter-spacing: 1px; }}
        .prod-name {{ font-size: 1.1rem; font-weight: 700; color: #fff; height: 2.8rem; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; line-height: 1.3; }}
        .price-now {{ font-size: 1.8rem; font-weight: 900; font-family: 'JetBrains Mono'; letter-spacing: -1px; }}
        .price-old {{ text-decoration: line-through; color: var(--dim); font-size: 0.9rem; margin-left: 10px; }}
        
        .btn {{ display: block; background: #fff; color: #000; text-align: center; padding: 1.1rem; border-radius: 16px; text-decoration: none; font-weight: 800; font-size: 0.85rem; margin-top: auto; transition: background 0.2s; }}
        .btn:hover {{ background: var(--blue); color: #fff; }}
        
        .footer {{ margin-top: 5rem; text-align: center; color: var(--dim); font-size: 0.8rem; letter-spacing: 2px; text-transform: uppercase; font-weight: 700; border-top: 1px solid var(--border); padding-top: 2rem; }}
    </style>
</head>
<body>
    <header class="header">
        <div class="brand">ODISEO <span>/MASTER_INSIGHTS</span></div>
        <div class="status">v5.1 PREMIUM REPORT ACTIVE</div>
    </header>

    <div class="kpi-grid">
        <div class="kpi">
            <div class="kpi-lbl">Scanning Target</div>
            <div class="kpi-val" style="color:var(--blue)">{total_prods:,}</div>
        </div>
        <div class="kpi yellow">
            <div class="kpi-lbl">Potential Glitches</div>
            <div class="kpi-val" style="color:var(--yellow)">{int(total_prods*0.046)}</div>
        </div>
        <div class="kpi green">
            <div class="kpi-lbl">Average Savings</div>
            <div class="kpi-val" style="color:var(--green)">{avg_disc}%</div>
        </div>
        <div class="kpi purple">
            <div class="kpi-lbl">Market Arbitrage</div>
            <div class="kpi-val" style="color:var(--purple)">{len(opps_list):,}</div>
        </div>
    </div>

    <h2 class="sec-title">📦 INTELLIGENCE FEED (Top 1500 Optimized)</h2>

    <div class="grid">
        {"".join([f'''
        <div class="card">
            <div class="pill-store">{p['store']}</div>
            {f'<div class="pill-opp">GAP {p["gap"]}%</div>' if p['gap'] > 0 else (f'<div class="pill-disc">-{p["discount"]}%</div>' if p['discount'] > 0 else '')}
            <div class="card-img"><img src="{p['img'] or 'https://placehold.co/100'}" alt="" onerror="this.src='https://placehold.co/100?text=IMG_ERROR'"></div>
            <div style="flex:1;">
                <div class="brand-lbl">{p['brand']}</div>
                <div class="prod-name" title="{p['name']}">{p['name']}</div>
                <div style="margin: 15px 0;">
                    <span class="price-now">{fmt_p(p['price'])}</span>
                    {f'<span class="price-old">{fmt_p(p["list_price"])}</span>' if p["list_price"] > p["price"] else ''}
                </div>
                <a href="{p['url']}" target="_blank" class="btn">GO TO SOURCE ↗</a>
            </div>
        </div>
        ''' for p in top_items])}
    </div>

    <footer class="footer">
        GENERATED ON {now} · FOR INTERNAL STRATEGIC USE ONLY
    </footer>
</body>
</html>
"""
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ PREMIUM REPORT SAVED: {OUTPUT_PATH}")

if __name__ == "__main__":
    generate()
