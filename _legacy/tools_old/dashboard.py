
import sqlite3
import pandas as pd
from datetime import datetime

def show_dashboard():
    db_path = "fravega_monitor.db"
    
    print("="*60)
    print(f" FRAVEGA SNIFFER - DASHBOARD [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
    print("="*60)
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Stats
            total_products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
            total_alerts = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
            
            print(f"Stats: {total_products} products tracked | {total_alerts} price alerts triggered.")
            
            # Recent Alerts (Filtering for more than $20k to avoid noise)
            print("\n🚨 RECENT PRICE DROPS (Min $20.000) 🚨")
            alerts_df = pd.read_sql_query("""
                SELECT p.title, a.old_price, a.new_price, a.timestamp
                FROM alerts a
                JOIN products p ON a.product_id = p.id
                WHERE a.new_price > 20000
                ORDER BY a.timestamp DESC
                LIMIT 15
            """, conn)
            
            if alerts_df.empty:
                print("No major alerts yet. The bot is watching high-ticket items.")
            else:
                for _, row in alerts_df.iterrows():
                    diff = row['old_price'] - row['new_price']
                    percent = (diff / row['old_price']) * 100
                    print(f"[{row['timestamp']}] {row['title']}")
                    print(f"    DROP: -${diff:.2f} ({percent:.1f}%) | Now: ${row['new_price']}")

            # Top Opportunities (Only for High-Ticket items over $100k)
            print("\n📈 CURRENT BEST OPPORTUNITIES (High-Ticket > $100.000) 📈")
            opps_df = pd.read_sql_query("""
                SELECT title, last_price, lowest_price
                FROM products
                WHERE last_price > 100000 AND last_price <= lowest_price
                ORDER BY last_price ASC
                LIMIT 10
            """, conn)
            
            if opps_df.empty:
                 print("Waiting for more high-ticket data...")
            else:
                for _, row in opps_df.iterrows():
                    print(f"- {row['title']}: ${row['last_price']} (Historical Low confirmed)")

    except Exception as e:
        print(f"Dashboard error (maybe DB not created yet?): {e}")

if __name__ == "__main__":
    show_dashboard()
