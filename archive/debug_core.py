import time
from intelligence_core import get_unified_data

print("Starting data fetch...")
start = time.time()
prods, cats = get_unified_data()
end = time.time()

print(f"Fetched {len(prods)} products in {end-start:.2f} seconds.")
if prods:
    print(f"First product sample: {prods[0]['name']} at {prods[0]['store']}")
else:
    print("NO PRODUCTS FOUND")
