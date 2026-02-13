
import json
import sys

def analyze_nuxt_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Nuxt data is usually just a list of values
    if isinstance(data, list):
        # Look for property related keywords
        keywords = ['Nexity', 'Bouygues', 'Kaufman', 'Appartement', 'Maison', 'Prix', '€']
        for keyword in keywords:
            print(f"--- Matches for '{keyword}' ---")
            for i, val in enumerate(data):
                if isinstance(val, str) and keyword.lower() in val.lower():
                    print(f"Index {i}: {val[:100]}")
    else:
        print("Data is not a list. Type:", type(data))

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else 'nuxt_data.json'
    analyze_nuxt_data(file_path)
