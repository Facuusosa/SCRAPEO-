
import requests
import json
import re

URL = "https://www.fravega.com/api/v1"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Referer": "https://www.fravega.com/"
}

# The categoryMenu API doesn't seem to give the full tree.
# But we know from 'next_data.json' analysis previously that there were 'categoryMenu' properties.
# Let's try to 'guess' top level categories or fetch a known list if possible.
# Actually, the 'items' query works by 'category' ID which often matches the slug.
# E.g. 'celulares-y-telefonos', 'tv-y-video'
# If we can just get a list of these, we are golden.
# Let's try to fetch home page and regex the links if the API is being stubborn about the tree.
# Or use the 'category' argument invalid value to see if it suggests values? It usually suggests 'Did you mean...?'
# But safer is to scan the HTML for links like '/l/...'

def extract_categories_from_html():
    print("Extracting Categories from Homepage HTML...")
    try:
        response = requests.get("https://www.fravega.com", headers=HEADERS)
        html = response.text
        
        # Regex for category links: /l/category-slug/ or /l/parent/child/
        pattern = r'href="/l/([^/"]+)/?"'
        matches = re.findall(pattern, html)
        
        unique_slugs = sorted(list(set(matches)))
        print(f"Found {len(unique_slugs)} unique category slugs from HTML.")
        
        categories = [{"slug": s, "id": s} for s in unique_slugs] # Assume ID = Slug
        
        # Save
        with open('extracted_categories.json', 'w') as f:
            json.dump(categories, f, indent=2)
            
        print("First 10 slugs found:")
        for s in unique_slugs[:10]:
            print(f"- {s}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    extract_categories_from_html()
