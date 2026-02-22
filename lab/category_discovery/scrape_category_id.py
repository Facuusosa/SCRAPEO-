
import requests
import json
import time

URL = "https://www.fravega.com/api/v1"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Referer": "https://www.fravega.com/"
}

# Confirmed: Category IDs are like '5a301bf51400002e004913e0'

# Strategy:
# Since we cannot easily get ALL category IDs via an API call (menu failed to give IDs),
# we have two options:
# 1. Scrape the HTML of category pages (like /l/celulares/) and find the ID in __NEXT_DATA__ or JS.
# 2. Use keyword search as the primary method for the bot (slower, less comprehensive).
# 3. Try to query `categoryMenu` again but use `category` type link if available? No, that failed.

# Let's try to scrape ONE category page to find its ID.
# If we can reliably get the ID from HTML, we can build a map.

def extract_category_id_from_url(slug):
    url = f"https://www.fravega.com/l/{slug}/"
    print(f"Scraping {url} for Category ID...")
    
    try:
        response = requests.get(url, headers=HEADERS)
        html = response.text
        
        # Look for "categoryId" or similar in the HTML
        # Often in tracking scripts or Next data.
        
        # In previously dumped next_data.json, we saw:
        # "categoryId": "celulares-y-telefonos" ? Wait, inspect analysis said:
        # "categoryMenu({"postalCode":""})"
        # But let's check if the ID appears in a pattern like "categoryId":"..."
        
        # Let's search for the ID format we saw: 24 hex chars.
        import re
        ids = re.findall(r'"categoryId":"([a-f0-9]{24})"', html)
        if ids:
            print(f"Found Category ID: {ids[0]}")
            return ids[0]
        
        # Also try "id":"..." 
        
        print("Could not find regex match for hex ID.")
        
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    # Test with a known slug
    extract_category_id_from_url("celulares-y-telefonos/celulares-liberados")
