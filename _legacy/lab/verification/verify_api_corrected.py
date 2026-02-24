
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
      slug
      listPrice { amounts { min max } }
      salePrice { amounts { min max } }
      skus {
          total
      }
    }
  }
}
"""

def verify_corrected():
    print("Verifying Corrected Product Listing API with Keyword Search...")
    try:
        response = requests.post(URL, json={'query': query}, headers=HEADERS)
        print(f"Status: {response.status_code}")
        
        try:
            data = response.json()
            if 'errors' in data:
                print("Errors:", json.dumps(data['errors'], indent=2))
            elif 'data' in data and 'items' in data['data']:
                total = data['data']['items']['total']
                products = data['data']['items']['results']
                print(f"Total Products: {total}")
                print(f"Fetched {len(products)} products.")
                if products:
                    print("Sample Product:", json.dumps(products[0], indent=2))
            else:
                print("Unexpected response:", data)
        except json.JSONDecodeError:
            print("Non-JSON response:", response.text[:200])

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    verify_corrected()
