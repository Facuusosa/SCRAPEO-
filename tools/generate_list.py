
import sqlite3
import json
import re

def clean_text(text):
    if not text: return ""
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def generate_list_view():
    db_path = "fravega_monitor.db"
    output_path = "catalogo_lista.html"

    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            products_rows = conn.execute("SELECT * FROM products ORDER BY lowest_price ASC").fetchall()

            # Pre-calculate data for JS to enable fast filtering
            data_list = []
            for row in products_rows:
                # Logic for status
                is_glitch = row['last_price'] < 5000 # Example glitch logic
                drop_pct = 0
                if row['list_price'] and row['list_price'] > row['last_price']:
                    drop_pct = ((row['list_price'] - row['last_price']) / row['list_price']) * 100
                
                item_id = row['sku_code'] if row['sku_code'] else row['id']

                data_list.append({
                    "id": row['id'],
                    "title": clean_text(row['title']),
                    "price": row['last_price'],
                    "old_price": row['list_price'], # Or use historical from alerts if needed
                    "is_glitch": is_glitch,
                    "drop_pct": int(drop_pct),
                    "image_url": row['image_url'],
                    "brand": row['brand_name'] or "GEN",
                    "category": row['category'] or "-",
                    "link": f"https://www.fravega.com/p/{row['slug']}-{item_id}/"
                })

    except Exception as e:
        print(f"Error extracting data: {e}")
        return

    # Load template
    try:
        with open("template_list.html", "r", encoding="utf-8") as f:
            template = f.read()
            
        final_html = template.replace("{DATA_JSON_PLACEHOLDER}", json.dumps(data_list))
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_html)
            
        print(f"✅ Dashboard Lista (Compacto) generado en: {output_path}")

    except Exception as e:
        print(f"Error generating HTML: {e}")

if __name__ == "__main__":
    generate_list_view()
