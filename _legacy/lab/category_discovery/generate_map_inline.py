
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

# Fix: Use NonEmptyString! type for variable.
# Wait, NonEmptyString is custom scalar. Standard clients usually map String to it.
# Maybe I should just inline the string to avoid type issues.

def generate_map_inline():
    print("Generating Category ID Map (Inline)...")
    
    KEYWORDS_MAP = {
        "Celulares": "celular samsung", 
        "Notebooks": "notebook",
        "TV": "tv smart",
        "Heladeras": "heladera",
        "Lavarropas": "lavarropas",
        "Aire": "aire acondicionado",
        "Consolas": "playstation",
        "Audio": "parlante"
    }
    
    final_map = {}
    
    for cat, kw in KEYWORDS_MAP.items():
        print(f"Mapping {cat} ({kw})...")
        
        # Inline the keyword to bypass variable type strictness
        query = f"""
        query ProductListing {{
          items(
            filtering: {{
              keywords: {{ query: "{kw}" }},
              active: true
            }}
          ) {{
            total
            results {{
              katalogCategoryId
              primaryCategoryId
              title
            }}
          }}
        }}
        """
        
        try:
            response = requests.post(URL, json={'query': query}, headers=HEADERS)
            data = response.json()
            
            if 'data' in data and data['data']['items']['results']:
                first = data['data']['items']['results'][0]
                uuid = first.get('katalogCategoryId') or first.get('primaryCategoryId')
                
                print(f"  -> Found ID: {uuid}")
                print(f"  -> Example: {first['title']}")
                
                final_map[cat] = {
                    "uuid": uuid,
                    "keyword": kw,
                    "example": first['title']
                }
            else:
                 print(f"  -> Failed. Response: {json.dumps(data.get('errors', 'No Item Results'))}")

        except Exception as e:
            print(f"  -> Error: {e}")
            
        time.sleep(1)

    with open('category_map.json', 'w') as f:
        json.dump(final_map, f, indent=2)
    print("\nMap saved to category_map.json")

if __name__ == "__main__":
    generate_map_inline()
