import requests
from bs4 import BeautifulSoup
import json
import concurrent.futures

def check_id(session, i):
    url = f"https://www.trouver-un-logement-neuf.com/recherche-neuf.html?search_type=promoteur&id_promoteur={i}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        r = session.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.title.string if soup.title else ""
            # Format: "SA BOUYGUES IMMOBILIER : immobilier neuf avec ..."
            if ":" in title:
                raw_name = title.split(":")[0].strip()
                # Clean prefix/suffix
                name = raw_name.replace("Immobilier neuf ", "").replace("SA ", "").strip()
                return i, name
    except Exception as e:
        print(f"Error ID {i}: {e}")
    return i, None

def build_map():
    mapping = {}
    print("Building promoter map (checking IDs 1-100)...")
    session = requests.Session()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(check_id, session, i) for i in range(1, 151)]
        for future in concurrent.futures.as_completed(futures):
            i, name = future.result()
            if name:
                print(f"ID {i}: {name}")
                mapping[name.upper()] = i
    
    with open('promoter_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    build_map()
