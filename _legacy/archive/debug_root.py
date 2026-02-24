import time
import intelligence_core

print("Starting data fetch...")
try:
    start = time.time()
    prods, cats = intelligence_core.get_unified_data()
    end = time.time()
    print(f"Fetched {len(prods)} products in {end-start:.2f} seconds.")
    if prods:
        print(f"First product sample: {prods[0]['name']} at {prods[0]['store']}")
    else:
        print("NO PRODUCTS FOUND")
except Exception as e:
    print(f"CORE FAILED: {e}")
