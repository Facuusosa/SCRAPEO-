
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
query ProductListing {
  items(
    filtering: {
      keywords: {
        query: "samsung"
      },
      active: true
    }
  ) {
    total
    results {
      id
      title
      katalogCategoryId
      primaryCategoryId
    }
  }
}
"""

def inspect_product_categories():
    print("Fetching product category IDs from KEYWORD search results...")
    try:
        response = requests.post(URL, json={'query': query}, headers=HEADERS)
        data = response.json()
        print(f"Status: {response.status_code}")
        
        if 'data' in data and data['data']['items']:
            products = data['data']['items']['results']
            print("Product Categories Found:")
            for p in products[:5]:
                print(f"- {p['title']}")
                print(f"  Katalog ID: {p.get('katalogCategoryId')}")
                print(f"  Primary ID: {p.get('primaryCategoryId')}")
        else:
            print("No data:", data)
    
    except Exception as e:
        print(e)
        
if __name__ == "__main__":
    inspect_product_categories()
