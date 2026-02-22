import os
import sys
import pandas as pd
from datetime import datetime

# Root path setup
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(root_dir, 'core', 'dashboard'))
from intelligence_core import get_unified_data

def export():
    print("📊 Extrayendo datos para exportación...")
    prods, cats = get_unified_data()
    
    if not prods:
        print("❌ No hay datos para exportar.")
        return

    df = pd.DataFrame(prods)
    
    # Limpiar y ordenar
    df = df[df['price'] > 500]
    df = df.sort_values(by=['gap', 'discount'], ascending=[False, False])
    
    # Formatear columnas
    cols = ['store', 'brand', 'name', 'price', 'list_price', 'discount', 'gap', 'cat', 'url', 'stock']
    df = df[cols]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"odiseo_market_data_{timestamp}.xlsx"
    output_path = os.path.join(root_dir, "output", filename)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"💾 Guardando {len(df)} productos en {filename}...")
    df.to_excel(output_path, index=False)
    print(f"✅ EXPORTACIÓN EXITOSA: {output_path}")

if __name__ == "__main__":
    try:
        export()
    except ImportError:
        print("❌ Error: Necesitas instalar pandas y openpyxl (pip install pandas openpyxl)")
    except Exception as e:
        print(f"❌ Error fatal en exportación: {e}")
