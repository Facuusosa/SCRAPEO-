
import requests
import json

URL = "https://www.fravega.com/api/v1"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Referer": "https://www.fravega.com/"
}

query = """
query listProducts($size: PositiveInt!, $offset: Int, $sorting: [SortOption!], $filtering: ItemFilteringInputType) {
  items(filtering: $filtering) {
    total
    results(
      size: $size
      buckets: [{sorting: $sorting, offset: $offset}]
    ) {
      id
      title
      slug
      skus {
        results {
          code
          pricing(channel: "fravega-ecommerce") {
            salePrice
            listPrice
            discount
          }
          stock {
            availability
          }
        }
      }
    }
  }
}
"""

def verify_definitive():
    print("Verifying DEFINITIVE Query Strategy (Simplified)...")
    
    variables = {
        "size": 10,
        "offset": 0,
        "sorting": "TOTAL_SALES_IN_LAST_30_DAYS",
        "filtering": {
            "categories": ["celulares/celulares-liberados"],
            "active": True,
            "salesChannels": ["fravega-ecommerce"]
        }
    }

    try:
        response = requests.post(URL, json={'query': query, 'variables': variables}, headers=HEADERS)
        data = response.json()
        
        if 'data' in data and data['data']['items']:
            total = data['data']['items']['total']
            products = data['data']['items']['results']
            print(f"✅ SUCCESS! Total Products Found: {total}")
            
            for p in products[:3]:
                print(f"  - {p['title']} (Slug: {p['slug']})")
                skus = p.get('skus', {}).get('results', [])
                if skus:
                    # Find first pricing that exists
                    price_info = skus[0].get('pricing', [])
                    if price_info:
                        price = price_info[0]
                        print(f"    Precio: ${price['salePrice']} | Lista: ${price['listPrice']} | Descuento: {price['discount']}%")
                    
                    stock = skus[0].get('stock', {})
                    print(f"    Stock: {'Disponible' if stock.get('availability') else 'Sin Stock'}")
        else:
            print("❌ Still failing:", json.dumps(data, indent=2))

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    verify_definitive()
