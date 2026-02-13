
from bs4 import BeautifulSoup
import json
import re
import sys

def extract_promoters(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    promoters = {} # { name: { id: pid, slug: slug } }
    
    # New pattern found: /programme-immobilier-neuf-promoteur-slug-id.html
    for a in soup.find_all('a', href=True):
        href = a['href']
        name_tag = a.find('span')
        name = name_tag.text.strip() if name_tag else a.text.strip()
        
        # Pattern: /programme-immobilier-neuf-promoteur-(.*)-(\d+)\.html
        m = re.search(r'promoteur-(.*)-(\d+)\.html', href)
        if m:
            slug = m.group(1)
            pid = m.group(2)
            if name and len(name) > 2:
                promoters[name] = {
                    'id': pid,
                    'slug': slug
                }
        
        # Also check for the other pattern just in case
        m2 = re.search(r'id_promoteur=(\d+)', href)
        if m2 and name not in promoters:
            pid = m2.group(1)
            # Try to get slug from href if possible
            slug_match = re.search(r'/promoteur/([^/?#]*)', href)
            slug = slug_match.group(1) if slug_match else name.lower().replace(' ', '-')
            if name and len(name) > 2:
                promoters[name] = {
                    'id': pid,
                    'slug': slug
                }

    return promoters

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else 'partenaires.html'
    promoters = extract_promoters(file_path)
    
    # Save to a mapping file
    with open('promoter_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(promoters, f, indent=2, ensure_ascii=False)
    
    print(f"Extracted {len(promoters)} promoters to promoter_mapping.json")
    # Print sorted by name
    for name in sorted(promoters.keys())[:10]:
        print(f"{name}: {promoters[name]}")
