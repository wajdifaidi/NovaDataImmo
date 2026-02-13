
import json
import requests
import re
from bs4 import BeautifulSoup
import sys
import time
import os

def extract_nuxt_data(html):
    # More robust extraction using regex
    pattern = r'<script id="__NUXT_DATA__"[^>]*>(.*?)</script>'
    match = re.search(pattern, html, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception as e:
            print(f"Error parsing Nuxt data: {e}")
    
    # Fallback to BeautifulSoup if regex fails
    soup = BeautifulSoup(html, 'html.parser')
    script = soup.find('script', id='__NUXT_DATA__')
    if script and script.string:
        try:
            return json.loads(script.string)
        except Exception as e:
            print(f"Error parsing Nuxt data via BS4: {e}")
    return None

def resolve_value(data, val_idx, depth=0):
    if depth > 10: # Increased limit for deeper Nuxt structures
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
    
    # Filter out common placeholders
    if isinstance(val, str) and val in ["No Data Available", "À définir"]:
        return None
        
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
                    if not status or status == "" or status == "Avant-Première" or status == "Lancement commercial":
                        mentions = prog.get('titre_mentions')
                        if mentions and mentions not in ["", "Avant-Première", "Lancement commercial"]:
                            status = mentions
                        else:
                            # Fallback to searching description for better status
                            desc = prog.get('descriptif', "")
                            if desc:
                                if any(k in desc for k in ["Travaux en cours", "Chantier en cours", "Démarrage des travaux"]):
                                    status = "Travaux en cours"
                                elif "Livraison immédiate" in desc or "Dernière opportunité" in desc:
                                    status = "Livraison immédiate"
                                elif "Lancement" in desc or "Nouveau" in desc:
                                    status = "Lancement commercial"
                                else:
                                    # Try to extract a delivery year if we still have nothing specific
                                    liv_match = re.search(r"Livraison (?:en )?(202[4-8])", desc)
                                    if liv_match:
                                        status = f"Livraison {liv_match.group(1)}"
                    
                    if not status or status == "":
                        status = "N/A"
                    
                    # Resolve City Info
                    city_data = prog.get('city')
                    city_name = "N/A"
                    dept_num = "N/A"
                    
                    def deep_resolve_string(v, data_arr, depth=0):
                        if depth > 10: return str(v)
                        if v is None: return "N/A"
                        if isinstance(v, int):
                            if 0 <= v < len(data_arr):
                                return deep_resolve_string(data_arr[v], data_arr, depth + 1)
                            return str(v)
                        if isinstance(v, dict):
                            # Recursively try to find a string in common name keys
                            for key in ['name', 'nom', 'label', 'text', 'ville_nom', 'departement_nom']:
                                if key in v:
                                    res = deep_resolve_string(v[key], data_arr, depth + 1)
                                    if res and res != "N/A" and not res.startswith('{'):
                                        return res
                            # If no name key found, but it has a value, try that
                            if 'value' in v:
                                res = deep_resolve_string(v['value'], data_arr, depth + 1)
                                if res and res != "N/A" and not res.startswith('{'):
                                    return res
                            # Last resort: just pick the first string-resolvable value that isn't a dict
                            for k, val in v.items():
                                if k not in ['id', 'kind', 'slug']:
                                    res = deep_resolve_string(val, data_arr, depth + 1)
                                    if res and res != "N/A" and not res.startswith('{'):
                                        return res
                            return "N/A"
                        return str(v)

                    if isinstance(city_data, dict):
                        city_name = deep_resolve_string(city_data.get('name'), data)
                        dept_num = deep_resolve_string(city_data.get('departement_num'), data)
                        if city_name == "N/A" and city_data.get('nom'):
                            city_name = deep_resolve_string(city_data.get('nom'), data)
                    elif isinstance(city_data, (str, int)):
                        city_name = deep_resolve_string(city_data, data)
                    
                    # Safety check for city_name that might still be a dict string
                    if city_name.startswith('{'):
                        # Try to parse and extract name
                        try:
                            import ast
                            d = ast.literal_eval(city_name)
                            if isinstance(d, dict):
                                for k in ['name', 'nom', 'label']:
                                    if k in d:
                                        city_name = deep_resolve_string(d[k], data)
                                        break
                        except: pass

                    units = []
                    # Fallback pricing and surface
                    prix_min = prog.get('prix_min') or prog.get('prix')
                    surface_min = prog.get('surface_min') or prog.get('superficie_min')
                    
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
                                                'etage': unit.get('etage'),
                                                'nb_unités': 1
                                            })
                                else:
                                    units.append({
                                        'typology': typology.get('typology'),
                                        'prix': typology.get('prix'),
                                        'superficie': typology.get('superficie'),
                                        'nbr_piece': typology.get('nbr_piece'),
                                        'nb_unités': 1
                                    })
                    
                    # Robust unit count fallback
                    prog_units = prog.get('nbrPiece') or prog.get('nbr_pieces') or 0
                    
                    properties.append({
                        'name': prog.get('nom'),
                        'city': city_name,
                        'dept_num': dept_num,
                        'cp': prog.get('cp'),
                        'statut': status,
                        'livraison': prog.get('livraison'),
                        'prix_min': prix_min,
                        'surface_min': surface_min,
                        'nbr_piece_total': prog_units,
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
