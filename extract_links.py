
from bs4 import BeautifulSoup
import json

def extract_links(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        links.append({
            'text': a.text.strip(),
            'href': a['href']
        })
    return links

if __name__ == "__main__":
    links = extract_links('home.html')
    # Filter links that might be related to promoters
    relevant = [l for l in links if 'promoteur' in l['href'].lower() or 'partenaire' in l['href'].lower() or 'promoteur' in l['text'].lower() or 'partenaire' in l['text'].lower()]
    
    for l in relevant:
        print(f"Text: {l['text']} | Href: {l['href']}")
    
    if not relevant:
        print("No relevant links found. Printing first 50 links:")
        for l in links[:50]:
            print(f"Text: {l['text']} | Href: {l['href']}")
