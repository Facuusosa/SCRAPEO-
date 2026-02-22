
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

# Slugs (leaf, full path, mixed) result in 0 total products.
# This strongly implies 'categories' filter expects numerical IDs or UUIDs.
# BUT we cannot easily get those IDs from the menu or previous API responses.
# The only place "katalogCategoryId" appeared was within the PRODUCT result itself.
# This means:
# 1. Search for "samsung"
# 2. Get products
# 3. Extract their category IDs.
# 4. Use those IDs to verify if they work in the 'categories' filter.
# If they do, then we confirm the filter needs UUIDs.
# Then the challenge becomes obtaining UUIDs for all categories.
# We can do this by searching keywords relevant to categories (e.g. "celular") and grabbing the ID of the first result's category.
# It's hacky but effective.

def verify_extracted_id():
    # ID extracted previously: 5a301bf51400002e004913e0 (from Adaptador Samsung)
    # This might be 'Accesorios de Celulares' or similar.
    # Let's try it.
    
    test_id = "5a301bf51400002e004913e0" 
    print(f"Testing Extracted Katalog ID: {test_id}")
    
    query = f"""
    query ProductListing {{
      items(
        filtering: {{
          categories: ["{test_id}"],
          active: true
        }}
      ) {{
        total
        results {{
            title
        }}
      }}
    }}
    """
    try:
         response = requests.post(URL, json={'query': query}, headers=HEADERS)
         data = response.json()
         if 'data' in data and data['data']['items']:
             total = data['data']['items']['total']
             print(f"  Success! Total: {total}")
             if total > 0:
                 print("  Sample:", data['data']['items']['results'][0]['title'])
         else:
             print(f"  Failed: {json.dumps(data.get('errors', 'Unknown'))}")
             
    except Exception as e:
        print(e)

if __name__ == "__main__":
    verify_extracted_id()
