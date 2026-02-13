
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

def resolve_value(data, val_idx, depth=0):
    if depth > 5: # Safety limit for recursion
        return val_idx
    
    if not isinstance(val_idx, int) or val_idx < 0 or val_idx >= len(data):
        return val_idx
    
    val = data[val_idx]
    
    if isinstance(val, dict):
        resolved_dict = {}
        for k, v in val.items():
            resolved_dict[k] = resolve_value(data, v, depth + 1)
        return resolved_dict
    elif isinstance(val, list):
        return [resolve_value(data, item, depth + 1) for item in val]
    
    return val

def parse_product(data, prod_idx):
    return resolve_value(data, prod_idx)

def get_promoter_properties(slug, pid):
    url = f"https://www.trouver-un-logement-neuf.com/programme-immobilier-neuf-promoteur-{slug}-{pid}.html"
    print(f"Fetching {url}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Failed to fetch {url}: {response.status_code}")
            return []
        
        html = response.text
        data = extract_nuxt_data(html)
        if not data:
            print("No Nuxt data found")
            return []
        
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
                    # Status extraction
                    status = prog.get('stock')
                    if not status or status == "":
                        status = prog.get('titre_mentions')
                    
                    # Resolve City Info
                    city_data = prog.get('city')
                    city_name = "N/A"
                    dept_num = "N/A"
                    if isinstance(city_data, dict):
                        city_name = city_data.get('name', "N/A")
                        dept_num = city_data.get('departement_num', "N/A")
                    elif isinstance(city_data, str):
                        city_name = city_data
                    
                    units = []
                    if 'types' in prog and isinstance(prog['types'], list):
                        for typology in prog['types']:
                            if isinstance(typology, dict):
                                details = typology.get('details')
                                if isinstance(details, list):
                                    for unit in details:
                                        if isinstance(unit, dict):
                                            units.append({
                                                'typology': typology.get('typology') or unit.get('type'),
                                                'prix': unit.get('prix'),
                                                'superficie': unit.get('superficie'),
                                                'nbr_piece': typology.get('nbr_piece') or unit.get('nbr_piece'),
                                                'etage': unit.get('etage')
                                            })
                                else:
                                    units.append({
                                        'typology': typology.get('typology'),
                                        'prix': typology.get('prix'),
                                        'superficie': typology.get('superficie'),
                                        'nbr_piece': typology.get('nbr_piece')
                                    })
                    
                    properties.append({
                        'name': prog.get('nom'),
                        'city': city_name,
                        'dept_num': str(dept_num),
                        'cp': prog.get('cp'),
                        'statut': status,
                        'livraison': prog.get('livraison'),
                        'link': f"https://www.trouver-un-logement-neuf.com{prog.get('link')}" if prog.get('link') else None,
                        'visual': prog.get('visual'),
                        'description': prog.get('descriptif'),
                        'units': units
                    })
        
        return properties
    except Exception as e:
        print(f"Error scraping {slug}: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    target = sys.argv[1].lower() if len(sys.argv) > 1 else 'nexity'
    
    mapping_file = 'promoter_mapping.json'
    if not os.path.exists(mapping_file):
        print(f"Error: {mapping_file} not found.")
        sys.exit(1)
        
    with open(mapping_file, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    
    found = False
    for name, info in mapping.items():
        if target in name.lower() or target in info['slug'].lower():
            res = get_promoter_properties(info['slug'], info['id'])
            print(f"Scraped {len(res)} properties for {name}")
            
            output_file = f"properties_{info['slug']}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(res, f, indent=2, ensure_ascii=False)
            print(f"Results saved to {output_file}")
            found = True
            break
    
    if not found:
        print(f"Promoter '{target}' not found in mapping")
