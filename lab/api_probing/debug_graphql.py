
import requests
import json

URL = "https://fen-gateway.fravega.com/graphql"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def test_query(name, fragment):
    query = f"""
    query listProducts($size: PositiveInt!, $offset: Int, $sorting: [SortOption!], $filtering: ItemFilteringInputType) {{
      items(filtering: $filtering) {{
        results(size: $size, buckets: [{{sorting: $sorting, offset: $offset}}]) {{
          title
          {fragment}
        }}
      }}
    }}
    """
    variables = {
        "size": 1,
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
        if 'errors' in data:
            print(f"❌ {name}: {data['errors'][0]['message']}")
        else:
            print(f"✅ {name}: Success!")
            print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"⚠️ {name}: Error {e}")

if __name__ == "__main__":
    # Test 1: Images at Product Level
    test_query("Product Images", "images { urls }")
    
    # Test 2: Multimedia at Product Level
    test_query("Product Multimedia", "multimedia { images { urls } }")

    # Test 3: SKU fields guess
    test_query("SKU Images Direct", "skus { results { images } }") # We know this returns [] but let's confirm structure
    
    # Test 4: SKU with 'medias'
    test_query("SKU Medias", "skus { results { medias { url } } }")

    # Test 5: SKU with 'pictures'
    test_query("SKU Pictures", "skus { results { pictures { url } } }")
    
