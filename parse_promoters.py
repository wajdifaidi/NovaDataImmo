
from bs4 import BeautifulSoup
import json
import re

def parse_promoters(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    promoters = {}
    
    # Look for links that look like /promoteur/slug-id.html
    # Some sites use different patterns, let's look for all links
    links = soup.find_all('a', href=re.compile(r'/promoteur/|id_promoteur='))
    
    for link in links:
        href = link.get('href', '')
        name = link.text.strip()
        
        # Pattern 1: /promoteur/bouygues-immobilier-8.html
        m1 = re.search(r'/promoteur/.*-(\d+)\.html', href)
        if m1:
            pid = m1.group(1)
            if name and name not in ["", "Habiter", "Investir"]:
                promoters[name] = pid
        
        # Pattern 2: ?id_promoteur=8
        m2 = re.search(r'id_promoteur=(\d+)', href)
        if m2:
            pid = m2.group(1)
            if name and name not in ["", "Habiter", "Investir"]:
                promoters[name] = pid

    # Also look in nuxt data if present (it should be since it's a Nuxt app)
    # The promoters list page might have the data in a cleaner way
    
    return promoters

if __name__ == "__main__":
    promoters = parse_promoters('promoters_list.html')
    
    with open('promoter_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(promoters, f, indent=2, ensure_ascii=False)
    
    print(f"Extracted {len(promoters)} promoters to promoter_mapping.json")
    for name, pid in list(promoters.items())[:10]:
        print(f"{name}: {pid}")
