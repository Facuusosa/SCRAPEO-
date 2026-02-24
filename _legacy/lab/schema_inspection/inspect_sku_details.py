
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
  StockAvailability: __type(name: "StockAvailability") {
    fields { name type { name kind } }
  }
  Sku: __type(name: "Sku") {
    fields { 
      name 
      type { 
        ofType {
          ofType {
            name
            fields { name }
          }
        }
      } 
    }
  }
}
"""

def inspect_sku_details():
    print("Introspecting StockAvailability and Pricing...")
    try:
        response = requests.get(URL, params={'query': query}, headers=HEADERS)
        data = response.json()
        
        # Parse StockAvailability
        if data['data']['StockAvailability']:
            print("StockAvailability Fields:")
            for f in data['data']['StockAvailability']['fields']:
                print(f"  - {f['name']}: {f['type']['name'] or f['type']['kind']}")
        
        # Parse Pricing field from Sku
        sku_fields = data['data']['Sku']['fields']
        pricing_field = next((f for f in sku_fields if f['name'] == 'pricing'), None)
        if pricing_field:
            print("Pricing Inner Type:")
            # pricing is NON_NULL -> LIST -> NON_NULL -> OBJECT
            # so ofType -> ofType -> ofType (type)
            # The query above only went 2 levels deep in generic 'type' field which is messy.
            # But let's see what we got.
            pass
            
            # Let's verify 'pricing' inner fields if possible
            # The query for Sku above gets 'type' which is the List wrapper...
            # I need ofType.ofType.ofType to get the inner object type name.
            
    except Exception as e:
        print(f"Exception: {e}")

# Revised query to specifically target pricing inner type
query_pricing = """
{
  __type(name: "Sku") {
    fields {
      name
      type {
        ofType {
          ofType {
            ofType {
              name
              kind
              fields { name }
            }
          }
        }
      }
    }
  }
}
"""

def inspect_pricing_type():
    print("Introspecting Sku.pricing inner type...")
    try:
        response = requests.get(URL, params={'query': query_pricing}, headers=HEADERS)
        data = response.json()
        fields = data['data']['__type']['fields']
        pricing = next((f for f in fields if f['name'] == 'pricing'), None)
        if pricing:
            inner = pricing['type']['ofType']['ofType']['ofType'] # NON_NULL -> LIST -> NON_NULL -> OBJECT
            print(f"Pricing Inner Type: {inner['name']}")
            print("Fields:", [f['name'] for f in inner.get('fields', [])])

        net_pricing = next((f for f in fields if f['name'] == 'netPricing'), None)
        if net_pricing:
            inner = net_pricing['type']['ofType']['ofType']['ofType']
            print(f"Net Pricing Inner Type: {inner['name']}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    inspect_sku_details()
    inspect_pricing_type()
