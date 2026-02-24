
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
{
  __type(name: "Query") {
    fields {
      name
      args {
        name
        type {
          name
          kind
          ofType {
            name
            kind
            ofType {
              name
              kind
            }
          }
        }
      }
      type {
        name
        kind
        ofType {
          name
          kind
        }
      }
    }
  }
}
"""

def fetch_schema():
    print("Fetching Query schema...")
    try:
        response = requests.get(URL, params={'query': query}, headers=HEADERS)
        data = response.json()
        
        # Filter for 'items' field
        fields = data['data']['__type']['fields']
        items_field = next((f for f in fields if f['name'] == 'items'), None)
        
        if items_field:
            with open('items_field_schema.json', 'w') as f:
                json.dump(items_field, f, indent=2)
            print("Saved items field schema to items_field_schema.json")
        else:
            print("Could not find 'items' field in Query.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_schema()
