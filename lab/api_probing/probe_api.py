
import requests
import json
import time

BASE_URL = "https://www.fravega.com"
ENDPOINTS = [
    "/api/v1",
    "/api/v1/rest",
    "/api/v1/rest/categories",
    "/api/v1/search?query=tv",
    "/api/product/search",
    "/chk-api/api/v1"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.fravega.com/"
}

def probe_apis():
    print("Starting API Probe...")
    results = {}
    
    for endpoint in ENDPOINTS:
        url = BASE_URL + endpoint
        print(f"Testing {url}...")
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            status = response.status_code
            print(f"Status: {status}")
            
            try:
                content = response.json()
                results[endpoint] = {"status": status, "json_response": content}
                print("JSON response captured.")
            except json.JSONDecodeError:
                content = response.text[:200]  # First 200 chars
                results[endpoint] = {"status": status, "text_response": content}
                print("Non-JSON response.")
                
        except Exception as e:
            print(f"Error connecting to {url}: {e}")
            results[endpoint] = {"error": str(e)}
        
        time.sleep(1) # Be polite

    with open('api_probe_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("Probe complete. Results saved to api_probe_results.json")

if __name__ == "__main__":
    probe_apis()
