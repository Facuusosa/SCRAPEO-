
import requests
import json
import urllib.parse

URL = "https://www.fravega.com/api/v1"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Referer": "https://www.fravega.com/"
}

def run_query(label, query, variables=None):
    print(f"\n--- Testing {label} ---")
    payload = {'query': query}
    if variables:
        payload['variables'] = variables
        
    try:
        # Try GET first as per error message "GET query missing"
        # But for complex queries POST is often supported too?
        # The error said "GET query missing", implying it expects GET parameters.
        # Let's try GET with query string.
        
        response = requests.get(URL, params=payload, headers=HEADERS)
        print(f"Status: {response.status_code}")
        try:
            data = response.json()
            if 'errors' in data:
                print("GraphQL Errors:", json.dumps(data['errors'], indent=2))
            else:
                print("Success!")
                # Print structure keys
                if 'data' in data:
                    print("Data keys:", data['data'].keys())
                    if 'items' in data['data'] and data['data']['items']:
                         print("Items keys:", data['data']['items'].keys())
                         if 'items' in data['data']['items']:
                             products = data['data']['items']['items']
                             print(f"Found {len(products)} products")
                             if len(products) > 0:
                                 print("First product sample:", json.dumps(products[0], indent=2))
        except json.JSONDecodeError:
            print("Response not JSON:", response.text[:200])

    except Exception as e:
        print(f"Exception: {e}")

introspection_query = """
    query {
        __schema {
            types {
                name
            }
        }
    }
"""

# Guessing 'searchTerm' based on typical e-commerce patterns if not 'category'
# Also trying to match the Apollo key structure
category_query = """
    query {
        items(
            filtering: {
                active: true,
                availableStock: { includeThousands: true },
                category: { id: ["celulares-y-telefonos", "celulares-liberados"] },
                tags: []
            }
        ) {
            items {
                id
                name
                sku
                salePrice
                listPrice
                images {
                    url
                }
            }
            total
        }
    }
"""

if __name__ == "__main__":
    run_query("Introspection", introspection_query)
    run_query("Category Listing", category_query)
