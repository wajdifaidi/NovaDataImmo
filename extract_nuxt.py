
import json
from bs4 import BeautifulSoup
import sys

def extract_nuxt_data(file_path, output_path='nuxt_data.json'):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    script = soup.find('script', id='__NUXT_DATA__')
    
    if script:
        try:
            data = json.loads(script.string)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Data extracted from {file_path} to {output_path}")
        except Exception as e:
            print(f"Error parsing script: {e}")
    else:
        print(f"No __NUXT_DATA__ found in {file_path}")

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else 'partenaires.html'
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'nuxt_data.json'
    extract_nuxt_data(file_path, output_path)
