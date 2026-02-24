
import requests
import json
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def clean_categories():
    print("Extracting and Cleaning Categories...")
    try:
        response = requests.get("https://www.fravega.com", headers=HEADERS)
        html = response.text
        
        # Look for the Mega Menu structure in HTML if possible.
        # Often it's in a <script id="__NEXT_DATA__"> which we already dumped once.
        # Let's re-examine the next_data.json but look specifically for the menu data which might be deep.
        # Or better, regex specifically for /l/category/subcategory structure.
        
        # Regex for strictly slugs: /l/slug/ or /l/slug/subslug/
        # We capture the full path after /l/
        matches = re.findall(r'href="/l/([^"?]+)/?"', html)
        
        unique_paths = sorted(list(set(matches)))
        print(f"Found {len(unique_paths)} unique paths.")
        
        # Filter out promotional paths starting with ?
        clean_paths = [p for p in unique_paths if not p.startswith('?')]
        print(f"Clean paths: {len(clean_paths)}")
        
        # Save
        with open('clean_categories.json', 'w') as f:
            json.dump(clean_paths, f, indent=2)
            
        print("Sample clean paths:")
        for p in clean_paths[:20]:
            print(f"- {p}")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    clean_categories()
