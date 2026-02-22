
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
  Sku: __type(name: "Sku") {
    name
    fields {
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
  }
}
"""

def verify_sku_fields():
    print("Introspecting Sku type...")
    try:
        response = requests.get(URL, params={'query': query}, headers=HEADERS)
        data = response.json()
        
        if 'data' in data and data['data']['Sku']:
            for f in data['data']['Sku']['fields']:
                ftype = f['type']['name'] or f['type']['kind']
                if f['type']['ofType']:
                    ftype += " -> " + (f['type']['ofType']['name'] or f['type']['ofType']['kind'])
                    if f['type']['ofType']['ofType']:
                        ftype += " -> " + (f['type']['ofType']['ofType']['name'] or f['type']['ofType']['ofType']['kind'])
                print(f"  - {f['name']}: {ftype}")
        else:
            print("Type Sku not found/accessible.")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    verify_sku_fields()
