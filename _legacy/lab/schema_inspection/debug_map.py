
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

# The previous script failed silently for all keywords.
# This likely means the payload logic was slightly off, possibly the query string interpolation
# or the structure of the query itself.
# Let's fix it by using f-strings for the whole query body to ensure correct JSON.
# Wait, previous script used `json={'query': query, 'variables': vars}` which is correct for GraphQL.
# Maybe `keywords: { query: $query }` needs `active: true`? Yes, I had `active: true`.
# Let's debug by printing the error response.

def generate_map_debug():
    print("Generating Category ID Map (Debug)...")
    
    # Just try one
    kw = "samsung"
    
    query = """
    query ProductListing($q: String!) {
      items(
        filtering: {
          keywords: { query: $q },
          active: true
        }
      ) {
        total
        results {
          katalogCategoryId
          title
        }
      }
    }
    """
    
    try:
        vars = {"q": kw}
        response = requests.post(URL, json={'query': query, 'variables': vars}, headers=HEADERS)
        data = response.json()
        
        if 'errors' in data:
            print("GraphQL Errors:", json.dumps(data['errors'], indent=2))
        elif 'data' in data:
            print(f"Success! Total: {data['data']['items']['total']}")
            if data['data']['items']['results']:
                print("First Result:", data['data']['items']['results'][0]['title'])
        else:
            print("Unknown response structure:", data)

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    generate_map_debug()
