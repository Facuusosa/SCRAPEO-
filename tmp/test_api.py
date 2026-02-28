import requests
import json

try:
    r = requests.get("http://localhost:3000/api/radar?limit=5")
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Items found: {len(data.get('items', []))}")
    print(f"Total: {data.get('total', 0)}")
    if data.get('items'):
        print(f"Sample: {data['items'][0]['name']}")
except Exception as e:
    print(f"Error: {e}")
