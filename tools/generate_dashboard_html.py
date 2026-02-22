import sqlite3
import pandas as pd
from datetime import datetime
import json

def generate_dashboard_html():
    db_path = "fravega_monitor.db"
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Obtener datos
            total_products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
            total_alerts = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
            
            # Alertas recientes
            alerts_df = pd.read_sql_query("""
                SELECT p.title, a.old_price, a.new_price, a.timestamp
                FROM alerts a
                JOIN products p ON a.product_id = p.id
                ORDER BY a.timestamp DESC
                LIMIT 50
            """, conn)
            
            # Mejores oportunidades
            opps_df = pd.read_sql_query("""
                SELECT title, last_price, lowest_price, category
                FROM products
                ORDER BY last_price DESC
                LIMIT 100
            """, conn)
            
            # Generar filas HTML para alertas
            alerts_html = ""
            for _, row in alerts_df.iterrows():
                diff = row['old_price'] - row['new_price']
                percent = (diff / row['old_price']) * 100 if row['old_price'] > 0 else 0
                status = "🔴" if diff > 0 else "🟢"
                alerts_html += f"""
                <tr>
                    <td>{status}</td>
                    <td>{row['title'][:50]}...</td>
                    <td>${row['old_price']:,.2f}</td>
                    <td>${row['new_price']:,.2f}</td>
                    <td style="color: {'red' if diff > 0 else 'green'}">${diff:+,.2f} ({percent:+.1f}%)</td>
                    <td>{row['timestamp']}</td>
                </tr>
                """
            
            # Generar filas HTML para productos
            products_html = ""
            for _, row in opps_df.iterrows():
                products_html += f"""
                <tr>
                    <td>{row['title'][:60]}...</td>
                    <td>${row['last_price']:,.2f}</td>
                    <td>${row['lowest_price']:,.2f}</td>
                    <td>{row['category']}</td>
                    <td style="color: {'green' if row['last_price'] <= row['lowest_price'] * 1.1 else 'black'}">{((row['last_price'] - row['lowest_price']) / row['lowest_price'] * 100) if row['lowest_price'] > 0 else 0:.1f}%</td>
                </tr>
                """
            
            # HTML Template
            html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Frávega Monitor - Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #667eea;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .timestamp {{
            color: #999;
            font-size: 14px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .stat-card h3 {{
            font-size: 14px;
            font-weight: 500;
            opacity: 0.9;
        }}
        
        .stat-card .number {{
            font-size: 32px;
            font-weight: bold;
            margin-top: 10px;
        }}
        
        .section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        
        h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 24px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        
        thead {{
            background: #f5f5f5;
            border-bottom: 2px solid #667eea;
        }}
        
        th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #333;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        
        tr:hover {{
            background: #f9f9f9;
        }}
        
        .status-alert {{
            font-size: 18px;
        }}
        
        .positive {{
            color: #27ae60;
            font-weight: bold;
        }}
        
        .negative {{
            color: #e74c3c;
            font-weight: bold;
        }}
        
        footer {{
            text-align: center;
            color: white;
            padding: 20px;
            opacity: 0.8;
        }}
        
        .search-box {{
            margin-bottom: 20px;
        }}
        
        input[type="text"] {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            table {{
                font-size: 12px;
            }}
            
            th, td {{
                padding: 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛒 FRÁVEGA SNIFFER - DASHBOARD</h1>
            <p class="timestamp">Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>📦 PRODUCTOS RASTREADOS</h3>
                    <div class="number">{total_products:,}</div>
                </div>
                <div class="stat-card">
                    <h3>🚨 ALERTAS GENERADAS</h3>
                    <div class="number">{total_alerts:,}</div>
                </div>
            </div>
        </header>
        
        <div class="section">
            <h2>📉 ALERTAS RECIENTES DE PRECIO</h2>
            <div class="search-box">
                <input type="text" id="alertFilter" placeholder="Buscar en alertas..." onkeyup="filterTable('alertsTable', this.value)">
            </div>
            <table id="alertsTable">
                <thead>
                    <tr>
                        <th>Estado</th>
                        <th>Producto</th>
                        <th>Precio Anterior</th>
                        <th>Precio Actual</th>
                        <th>Cambio</th>
                        <th>Fecha</th>
                    </tr>
                </thead>
                <tbody>
                    {alerts_html if alerts_html else '<tr><td colspan="6" style="text-align: center; color: #999;">No hay alertas disponibles</td></tr>'}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>📊 TODOS LOS PRODUCTOS MONITOREADOS</h2>
            <div class="search-box">
                <input type="text" id="productsFilter" placeholder="Buscar productos..." onkeyup="filterTable('productsTable', this.value)">
            </div>
            <table id="productsTable">
                <thead>
                    <tr>
                        <th>Producto</th>
                        <th>Precio Actual</th>
                        <th>Precio Mínimo Histórico</th>
                        <th>Categoría</th>
                        <th>% sobre Mínimo</th>
                    </tr>
                </thead>
                <tbody>
                    {products_html if products_html else '<tr><td colspan="5" style="text-align: center; color: #999;">No hay productos disponibles</td></tr>'}
                </tbody>
            </table>
        </div>
        
        <footer>
            <p>🤖 Bot de Monitoreo Autónomo | Sistema Frávega Sniffer V4.0</p>
            <p style="font-size: 12px; margin-top: 10px;">Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>
    
    <script>
        function filterTable(tableId, searchText) {{
            const table = document.getElementById(tableId);
            const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
            
            searchText = searchText.toLowerCase();
            
            for (let row of rows) {{
                let text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchText) ? '' : 'none';
            }}
        }}
        
        // Auto-refresh cada 30 segundos
        setTimeout(function() {{
            location.reload();
        }}, 30000);
    </script>
</body>
</html>
"""
            
            # Guardar HTML
            with open("dashboard.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            
            print("✅ Dashboard HTML generado: dashboard.html")
            print("📱 Abre el archivo en tu navegador para ver todos los materiales")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Asegúrate de que el sniffer esté generando la base de datos primero")
        return False

if __name__ == "__main__":
    generate_dashboard_html()
