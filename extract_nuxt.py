
import json
import re

def extract_nuxt_data(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    patterns = [
        r'<script id="__NUXT_DATA__"[^>]*>(.*?)</script>',
        r'<script type="application/json" id="__NUXT_DATA__"[^>]*>(.*?)</script>',
        r'__NUXT_DATA__.*?>(.*?)</script>'
    ]
    for pattern in patterns:
        m = re.search(pattern, html, re.DOTALL)
        if m:
            try: return json.loads(m.group(1))
            except: continue
    return None

def resolve_value(data, val_idx, depth=0):
    if depth > 5: return val_idx
    if not isinstance(val_idx, int) or val_idx < 0 or val_idx >= len(data): return val_idx
    val = data[val_idx]
    if isinstance(val, dict):
        return {k: resolve_value(data, v, depth + 1) for k, v in val.items()}
    elif isinstance(val, list):
        return [resolve_value(data, item, depth + 1) for item in val]
    return val

html_file = "c:/NovaDataImmo/nexity_promoter.html"
data = extract_nuxt_data(html_file)

if data:
    state_info = data[1]
    data_key = state_info.get('data')
    data_obj_idx = data[data_key][1] if isinstance(data[data_key], list) else data[data_key]
    data_obj = data[data_obj_idx]
    product_indices = []
    for key, val_idx in data_obj.items():
        if key.startswith('search-products:'):
            product_indices = data[val_idx]
            break
    
    print(f"Total products: {len(product_indices)}")
    found = 0
    for idx in product_indices:
        prod = resolve_value(data, idx)
        stock = prod.get('stock', '')
        mentions = prod.get('titre_mentions', '')
        desc = prod.get('descriptif', '')
        
        # Look for "Travaux" or "Livraison" in any of these fields
        is_interesting = False
        for s in [stock, mentions, desc]:
            if s and any(k in s for k in ["Travaux", "Livraison", "Vendu", "Dernière"]):
                is_interesting = True
                break
        
        if is_interesting:
            found += 1
            print(f"\nInteresting Product: {prod.get('nom')}")
            print(f"  stock: {stock}")
            print(f"  mentions: {mentions}")
            print(f"  desc (start): {desc[:100]}...")
            if found >= 10: break
else:
    print("Could not extract Nuxt data.")
