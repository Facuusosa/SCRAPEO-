
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
  ItemFilteringInputType: __type(name: "ItemFilteringInputType") {
    kind
    name
    inputFields {
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
  ItemSearchResponse: __type(name: "ItemSearchResponse") {
    kind
    name
    fields {
      name
      args {
        name
        type {
          name
          kind
        }
      }
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

def fetch_details():
    print("Fetching schema details...")
    try:
        response = requests.get(URL, params={'query': query}, headers=HEADERS)
        data = response.json()
        
        with open('schema_details.json', 'w') as f:
            json.dump(data['data'], f, indent=2)
        print("Details saved to schema_details.json")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_details()
