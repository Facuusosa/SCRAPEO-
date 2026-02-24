
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
  __type(name: "ItemSkuSearchResponse") {
    fields {
      name
      type {
        ofType {
           ofType {
             name
             kind
             fields {
               name
             }
           }
        }
      }
    }
  }
}
"""

def inspect_sku_inner():
    print("Introspecting ItemSkuSearchResponse -> results...")
    try:
        response = requests.get(URL, params={'query': query}, headers=HEADERS)
        data = response.json()
        # print(json.dumps(data, indent=2))
        
        fields = data['data']['__type']['fields']
        results_field = next((f for f in fields if f['name'] == 'results'), None)
        if results_field:
            inner_type = results_field['type']['ofType']['ofType']
            if inner_type:
                print(f"Inner Type Name: {inner_type.get('name')}")
                print(f"Inner Type Kind: {inner_type.get('kind')}")
                if inner_type.get('fields'):
                     print("Fields:", [f['name'] for f in inner_type['fields']])
            else:
                print("Inner type structure unknown")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    inspect_sku_inner()
