
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
  __type(name: "LinkUnion") {
    possibleTypes {
      name
      kind
    }
  }
}
"""

def inspect_union_types():
    print("Checking LinkUnion types again...")
    try:
        response = requests.get(URL, params={'query': query}, headers=HEADERS)
        data = response.json()
        types = data['data']['__type']['possibleTypes']
        print("Possible Types for LinkUnion:")
        for t in types:
            print(f"- {t['name']}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    inspect_union_types()
