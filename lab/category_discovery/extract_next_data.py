
import re
import json

def extract_next_data():
    try:
        with open('dump.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Regex to find the script tag content
        pattern = r'<script id="__NEXT_DATA__" type="application/json">([^<]+)</script>'
        match = re.search(pattern, html_content)
        
        if match:
            json_str = match.group(1)
            data = json.loads(json_str)
            
            # Save strictly the relevant parts to avoid huge file
            with open('next_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            print("Successfully extracted __NEXT_DATA__ to next_data.json")
            
            # Print keys to help with analysis
            print("Keys found:", list(data.keys()))
            if 'props' in data:
                print("Props keys:", list(data['props'].keys()))
                if 'pageProps' in data['props']:
                    print("PageProps keys:", list(data['props']['pageProps'].keys()))
        else:
            print("Could not find __NEXT_DATA__ in dump.html")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_next_data()
