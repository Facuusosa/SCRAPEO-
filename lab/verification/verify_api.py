
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
      categories: ["celulares-y-telefonos", "celulares-liberados"],
      active: true
    }
  ) {
    total
    results {
      id
      name
      sku
      images {
        url
      }
      price {
        salePrice
        listPrice
      }
    }
  }
}
"""

# Note: 'price' and 'images' fields are guesses. If they fail, I'll fallback to just id, name, sku.
# Based on Apollo state, 'images' and 'salePrice'/'listPrice' (flat fields) might be used.
# Let's try conservative query first, then expand.

query_conservative = """
query ProductListing {
  items(
    filtering: {
      categories: ["celulares-y-telefonos", "celulares-liberados"],
      active: true
    }
  ) {
    total
    results {
      id
      name
      sku
    }
  }
}
"""

def verify_api():
    print("Verifying Product Listing API...")
    try:
        response = requests.post(URL, json={'query': query_conservative}, headers=HEADERS)
        print(f"Status: {response.status_code}")
        
        try:
            data = response.json()
            if 'errors' in data:
                print("Errors:", json.dumps(data['errors'], indent=2))
            elif 'data' in data:
                total = data['data']['items']['total']
                products = data['data']['items']['results']
                print(f"Total Products: {total}")
                print(f"Fetched {len(products)} products.")
                if products:
                    print("Sample Product:", json.dumps(products[0], indent=2))
                
                # Save working query to file for future use
                with open('working_query.graphql', 'w') as f:
                    f.write(query_conservative)
            else:
                print("Unexpected response:", data)
                
        except json.JSONDecodeError:
            print("Non-JSON response:", response.text[:200])

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    verify_api()
