
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

# List of keywords to map to Category IDs
KEYWORDS = [
    {"display": "Celulares", "query": "celular samsung"},
    {"display": "Notebooks", "query": "notebook hp"},
    {"display": "TV", "query": "tv smart 50"},
    {"display": "Heladeras", "query": "heladera no frost"},
    {"display": "Lavarropas", "query": "lavarropas automatico"},
    {"display": "Aire Acondicionado", "query": "aire acondicionado split"},
    {"display": "Consolas", "query": "playstation 5"},
    {"display": "Tablets", "query": "tablet samsung"},
    {"display": "Smartwatches", "query": "smartwatch reloj"},
    {"display": "Audio", "query": "parlante bluetooth"}
]

query = """
query ProductListing($query: String!) {
  items(
    filtering: {
      keywords: { query: $query },
      active: true
    }
  ) {
    results {
      katalogCategoryId
      primaryCategoryId
      title
    }
  }
}
"""

def generate_map():
    print("Generating Category ID Map...")
    category_map = {}
    
    for k in KEYWORDS:
        kw = k["query"]
        display = k["display"]
        
        try:
            vars = {"query": kw}
            response = requests.post(URL, json={'query': query, 'variables': vars}, headers=HEADERS)
            data = response.json()
            
            if 'data' in data and data['data']['items']['results']:
                first_product = data['data']['items']['results'][0]
                cat_id = first_product.get('katalogCategoryId')
                
                print(f"Mapped '{display}' ({kw}) -> {cat_id}")
                print(f"  Example Product: {first_product['title']}")
                
                category_map[display] = {
                    "uuid": cat_id,
                    "keyword": kw,
                    "example_product": first_product['title']
                }
            else:
                print(f"Failed to map '{display}' ({kw})")

        except Exception as e:
            print(f"Error mapping {display}: {e}")
        
        time.sleep(1) # Polite delay

    with open('category_map.json', 'w') as f:
        json.dump(category_map, f, indent=2)
    print("\nCategory Map Saved to category_map.json")

if __name__ == "__main__":
    generate_map()
