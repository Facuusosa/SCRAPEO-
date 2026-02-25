import sqlite3
import os
import json

TARGETS_DIR = os.path.join(os.getcwd(), "data", "databases")

def analyze_raw_data():
    report = []
    if not os.path.exists(TARGETS_DIR):
        print("No data directory found.")
        return

    for db_file in os.listdir(TARGETS_DIR):
        if db_file.endswith(".db"):
            db_path = os.path.join(TARGETS_DIR, db_file)
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check for table structure
                cursor.execute("PRAGMA table_info(products)")
                cols = [c[1] for c in cursor.fetchall()]
                
                price_col = "last_price" if "last_price" in cols else "current_price"
                
                # Total products
                cursor.execute(f"SELECT COUNT(*) FROM products")
                total = cursor.fetchone()[0]
                
                # Products with some discount/gap info if available
                # Many monitor DBs have 'discount_pct' or we can check price < list_price
                has_list_price = "list_price" in cols
                
                deep_discounts = 0
                if has_list_price:
                    cursor.execute(f"SELECT COUNT(*) FROM products WHERE list_price > {price_col} * 1.1")
                    deep_discounts = cursor.fetchone()[0]
                
                report.append({
                    "retailer": db_file.split("_")[0],
                    "total": total,
                    "potential_discounts_10plus": deep_discounts
                })
                conn.close()
            except Exception as e:
                pass
    
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    analyze_raw_data()
