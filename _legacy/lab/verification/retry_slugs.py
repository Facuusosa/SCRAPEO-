
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

# The frontend code clearly had: "category": { "id": [...] }.
# But GraphQL fails saying "category" is not defined.
# This means the frontend uses a DIFFERENT GraphQL schema or query.
# OR I am hitting the wrong endpoint? No, next_data.json says api/v1.
# Maybe "category" is an alias? No, can't alias input fields.
# Maybe "categories" (plural) accepts objects? No, introspection says [String].
# Wait. `ItemFilteringInput` introspection showed `categories` as [String].
# But `next_data.json` had `category` not `categories`.
# Maybe the frontend data structure is mapped BEFORE sending to GraphQL.
# Maybe the frontend library (Apollo) transforms `category: {id: [slug]}` into `categories: [slug]`?
# If so, my call to verify_inline.py with `categories: ["slug"]` returning 0 results is still the mystery.
# Why does `categories: ["celulares-y-telefonos"]` return 0?
# Maybe the slug needs to be the LAST part only? Or FULL path?
# I tried both in verify_slugs.py (inline attempt failed due to python error, fixed now).
# Let's retry verify_inline.py CAREFULLY.
# And try variants of the slug.

def retry_slugs():
    print("Retrying Slugs with Variations...")
    
    variations = [
        ["celulares-y-telefonos"], # Top level
        ["celulares-liberados"],   # Leaf
        ["celulares-y-telefonos", "celulares-liberados"], # Both path
        ["celulares-y-telefonos/celulares-liberados"], # Joined
        ["Celulares y Telefonos"], # Name?
        ["Celulares Liberados"]
    ]
    
    for v in variations:
        ids_str = json.dumps(v)
        query = f"""
        query ProductListing {{
          items(
            filtering: {{
              categories: {ids_str},
              active: true
            }}
          ) {{
            total
          }}
        }}
        """
        try:
             response = requests.post(URL, json={'query': query}, headers=HEADERS)
             data = response.json()
             total = data.get('data', {}).get('items', {}).get('total', 'Error')
             print(f"Testing {v} -> Total: {total}")
             if total != 'Error' and total > 0:
                 print("  >>> WINNER FOUND!")
        except Exception as e:
            print(e)
        time.sleep(0.5)

if __name__ == "__main__":
    retry_slugs()
