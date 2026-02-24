
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
  LinkUnion: __type(name: "LinkUnion") {
    kind
    possibleTypes {
      name
      kind
      fields { name }
    }
  }
}
"""

def inspect_link_union():
    print("Introspecting LinkUnion...")
    try:
        response = requests.get(URL, params={'query': query}, headers=HEADERS)
        data = response.json()
        print(json.dumps(data['data'], indent=2))
        
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    inspect_link_union()
