
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
      links {
        ... on CategoryLink {
          id
          label
          href
        }
        ... on SimpleLink {
          id
          label
          href
        }
      }
    }
  }
}
"""

def fetch_menu_full():
    print("Fetching Complete Category Menu...")
    try:
        response = requests.post(URL, json={'query': query}, headers=HEADERS)
        print(f"Status: {response.status_code}")
        
        try:
            data = response.json()
            if 'errors' in data:
                 print("Errors:", json.dumps(data['errors'], indent=2))
            elif 'data' in data and 'categoryMenu' in data['data']:
                 menu = data['data']['categoryMenu']
                 print(f"Top Level Items: {len(menu)}")
                 
                 with open('final_category_map.json', 'w') as f:
                     json.dump(menu, f, indent=2)
                 print("Categories saved to final_category_map.json")

            else:
                 print("No categoryMenu data found.")

        except json.JSONDecodeError:
             print("Non-JSON response.")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    fetch_menu_full()
