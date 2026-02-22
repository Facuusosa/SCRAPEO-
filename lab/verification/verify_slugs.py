
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

query = """
query ProductListing($categories: [String!]) {
  items(
    filtering: {
      categories: $categories,
      active: true
    }
  ) {
    total
    results {
      id
      title
      slug
      skus {
        results {
          code
          stock { availability }
          pricing { salePrice listPrice }
        }
      }
    }
  }
}
"""

def verify_category_slugs():
    print("Verifying if Slugs work as Category IDs...")
    
    with open('clean_categories.json', 'r') as f:
        paths = json.load(f)
    
    # Take a sample of 5 paths
    sample_paths = [p.strip('/') for p in paths[:5]]
    # Also manual ones that are complex like 'audio/auriculares'
    # API usually needs the leaf slug or the full path? Let's try both.
    
    results = {}
    
    for path in sample_paths:
        slug = path.split('/')[-1] # Try leaf
        print(f"Testing slug: {slug} (from {path})")
        
        try:
            vars = {"categories": [slug]}
            response = requests.post(URL, json={'query': query, 'variables': vars}, headers=HEADERS)
            data = response.json()
            
            if 'data' in data and data['data']['items']:
                total = data['data']['items']['total']
                print(f"  Success! Total: {total}")
                results[slug] = total
            else:
                print(f"  Failed: {json.dumps(data.get('errors', 'Unknown'))}")
                
        except Exception as e:
            print(f"Exception: {e}")
        
        time.sleep(1)

    print("\nAttempting full path for nested...")
    nested = "audio/auriculares"
    print(f"Testing full path: {nested}")
    try:
        vars = {"categories": [nested]}
        response = requests.post(URL, json={'query': query, 'variables': vars}, headers=HEADERS)
        data = response.json()
        if 'data' in data and data['data']['items']:
             print(f"  Success with full path! Total: {data['data']['items']['total']}")
        else:
             print("  Failed with full path.")
             # Try split
             parts = nested.split('/')
             print(f"  Trying individual parts: {parts}")
             vars = {"categories": parts}
             response = requests.post(URL, json={'query': query, 'variables': vars}, headers=HEADERS)
             print(f"  Result: {response.json().get('data', {}).get('items', {}).get('total', 'Error')}")

    except Exception as e:
        print(e)

if __name__ == "__main__":
    verify_category_slugs()
