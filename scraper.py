
import json
import requests
import re
from bs4 import BeautifulSoup
import sys
import time
import os

def extract_nuxt_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    script = soup.find('script', id='__NUXT_DATA__')
    if script:
        try:
            return json.loads(script.string)
        except Exception as e:
            print(f"Error parsing Nuxt data: {e}")
    return None

def parse_product(data, prod_idx):
    # data is the Nuxt list
    # prod_idx is the index of the product object/map
    product_map = data[prod_idx]
    if not isinstance(product_map, dict):
        return None
    
    parsed = {}
    for key, val_idx in product_map.items():
        if isinstance(val_idx, int) and val_idx < len(data):
            val = data[val_idx]
            # Handle list of indices (like medias or types)
            if isinstance(val, list) and len(val) > 0 and isinstance(val[0], int):
                # For simplicity, we might just store the first one or keep the list
                parsed[key] = val
            else:
                parsed[key] = val
        else:
            parsed[key] = val_idx
            
    return parsed

def get_promoter_properties(slug, pid):
    url = f"https://www.trouver-un-logement-neuf.com/programme-immobilier-neuf-promoteur-{slug}-{pid}.html"
    print(f"Fetching {url}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch {url}: {response.status_code}")
            return []
        
        html = response.text
        data = extract_nuxt_data(html)
        if not data:
            print("No Nuxt data found")
            return []
        
        # Find the product list key
        # Under data[1]['data'] we find the keys for the current page
        state_info = data[1]
        data_key = state_info.get('data')
        if data_key is None:
            return []
        
        data_obj_idx = data[data_key][1] if isinstance(data[data_key], list) else data[data_key]
        data_obj = data[data_obj_idx]
        
        product_indices = []
        for key, val_idx in data_obj.items():
            if key.startswith('search-products:'):
                product_indices = data[val_idx]
                break
        
        if not product_indices:
            print("No search-products found in Nuxt data")
            return []
        
        properties = []
        for idx in product_indices:
            if isinstance(idx, int) and idx < len(data):
                prog = parse_product(data, idx)
                if prog:
                    # Clean up the program data
                    # nbrPiece, city, visual, link, nom, descriptif, livraison
                    # types is a list of unit indices
                    units = []
                    if 'types' in prog and isinstance(prog['types'], list):
                        for u_idx in prog['types']:
                            unit = parse_product(data, u_idx)
                            if unit:
                                units.append({
                                    'typology': unit.get('typology'),
                                    'prix': unit.get('prix'),
                                    'superficie': unit.get('superficie'),
                                    'nbr_piece': unit.get('nbr_piece')
                                })
                    
                    properties.append({
                        'name': prog.get('nom'),
                        'city': prog.get('city'),
                        'cp': prog.get('cp'),
                        'livraison': prog.get('livraison'),
                        'link': f"https://www.trouver-un-logement-neuf.com{prog.get('link')}" if prog.get('link') else None,
                        'visual': prog.get('visual'),
                        'description': prog.get('descriptif'),
                        'units': units
                    })
        
        return properties
    except Exception as e:
        print(f"Error scraping {slug}: {e}")
        return []

if __name__ == "__main__":
    # Example usage: py scraper.py nexity
    target = sys.argv[1].lower() if len(sys.argv) > 1 else 'nexity'
    
    with open('promoter_mapping.json', 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    
    found = False
    for name, info in mapping.items():
        if target in name.lower() or target in info['slug'].lower():
            res = get_promoter_properties(info['slug'], info['id'])
            print(f"Scraped {len(res)} properties for {name}")
            
            # Save results
            output_file = f"properties_{info['slug']}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(res, f, indent=2, ensure_ascii=False)
            print(f"Results saved to {output_file}")
            found = True
            break
    
    if not found:
        print(f"Promoter '{target}' not found in mapping")
