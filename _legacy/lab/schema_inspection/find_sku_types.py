
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
{
  __schema {
    types {
      name
    }
  }
}
"""

def find_sku_types():
    print("Finding SKU related types...")
    try:
        response = requests.get(URL, params={'query': query}, headers=HEADERS)
        data = response.json()
        
        types = [t['name'] for t in data['data']['__schema']['types'] if t['name'] and 'Sku' in t['name']]
        print("Types with 'Sku':")
        for t in types:
            print(f"- {t}")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    find_sku_types()
