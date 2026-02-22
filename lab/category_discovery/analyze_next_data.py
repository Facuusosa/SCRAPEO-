
import json

def analyze_json():
    try:
        with open('next_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # print("--- Runtime Config ---")
        # if 'runtimeConfig' in data:
        #     for k, v in data['runtimeConfig'].items():
        #         print(f"{k}: {v}")

        print("\n--- ROOT_QUERY keys ---")
        if 'props' in data and 'pageProps' in data['props'] and '__APOLLO_STATE__' in data['props']['pageProps']:
            apollo_state = data['props']['pageProps']['__APOLLO_STATE__']
            
            if 'ROOT_QUERY' in apollo_state:
                keys = list(apollo_state['ROOT_QUERY'].keys())
                for k in keys:
                    print(k)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_json()
