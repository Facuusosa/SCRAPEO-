
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

# The introspection showed ItemFilteringInputType -> categories -> [NonEmptyString!]!
# But maybe we need to pass categories directly in the query, not as variable?
# The error "Variable '$categories' of type '[String!]' used in position expecting type '[NonEmptyString!]!'" suggests a type mismatch.
# NonEmptyString is a custom scalar. String! is standard scalar. They might not be compatible automatically.
# Let's try inline literal list first.

def verify_inline_slugs():
    print("Verifying Slugs with Inline List...")
    
    slugs = ["celulares-y-telefonos", "celulares-liberados"]
    slugs_str = json.dumps(slugs)
    
    query = f"""
    query ProductListing {{
      items(
        filtering: {{
          categories: {slugs_str},
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
        print(f"Testing {slugs}")
        if 'data' in data and data['data']['items']:
            print(f"  Success! Total: {data['data']['items']['total']}")
        else:
            print(f"  Failed: {json.dumps(data.get('errors', 'Unknown'))}")
            
    except Exception as e:
        print(f"Exception: {e}")

    # Try single slug
    slugs = ["audio"]
    slugs_str = json.dumps(slugs)
    query = f"""
    query ProductListing {{
      items(
        filtering: {{
          categories: {slugs_str},
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
        print(f"Testing {slugs}")
        if 'data' in data and data['data']['items']:
            print(f"  Success! Total: {data['data']['items']['total']}")
        else:
             print(f"  Failed.")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    verify_inline_slugs()
