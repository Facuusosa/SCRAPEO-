
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
query CategoryMenu {
  categoryMenu(postalCode: "1414") {
    id
    label
    sections {
      id
      label
      items {
        ... on GenericLink {
          id
          label
          href
        }
        ... on ListingLink {
          id
          label
          href
        }
        ... on LandingLink {
          id
          label
          # href is missing, seemingly 'label' or 'context' or 'id' is unique part.
          # Let's inspect 'context' if needed later, but for now ID and Label might suffice.
        }
        ... on ModalLink {
          id
          label
        }
      }
    }
  }
}
"""

def fetch_menu_final():
    print("Fetching Complete Category Menu (Final Fixed)...")
    try:
        response = requests.post(URL, json={'query': query}, headers=HEADERS)
        print(f"Status: {response.status_code}")
        
        try:
            data = response.json()
            if 'errors' in data:
                 print("Errors:", json.dumps(data['errors'], indent=2))
            elif 'data' in data and data['data']['categoryMenu']:
                 menu = data['data']['categoryMenu']
                 print(f"Top Level Items: {len(menu)}")
                 
                 with open('final_category_map.json', 'w') as f:
                     json.dump(menu, f, indent=2)
                 print("Categories saved to final_category_map.json")
                 
                 links = []
                 for sec in menu:
                     if sec.get('sections'):
                         for s in sec['sections']:
                             if s.get('items'):
                                 for i in s['items']:
                                     # Not all have href now
                                     if 'href' in i:
                                         links.append(i)
                                     elif i.get('label'):
                                         links.append(i) # For LandingLinks just include them
                 
                 print(f"Total Navigable Items Found: {len(links)}")
                 if links:
                     print("Sample Links:")
                     for l in links[:5]:
                         href = l.get('href') or "N/A"
                         print(f"- {l.get('label')} -> {href}")

            else:
                 print("No categoryMenu data found.")

        except json.JSONDecodeError:
             print("Non-JSON response.")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    fetch_menu_final()
