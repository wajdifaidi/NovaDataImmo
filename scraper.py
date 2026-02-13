import requests
import json
import pandas as pd
from datetime import datetime
import os

def scrape_nexity():
    print("Starting Algolia-based extraction (Target: 332 programs)...")
    app_id = "04QRMGY2OL"
    api_key = "31bd735badd4f77d8e2dc769e29d8d04"
    index_name = "prod_bien"
    
    url = f"https://{app_id}-dsn.algolia.net/1/indexes/*/queries"
    
    params = {
        "x-algolia-agent": "Algolia for JavaScript (4.13.1); Browser",
        "x-algolia-api-key": api_key,
        "x-algolia-application-id": app_id
    }
    
    # Payload for 'neuf france' (518 results)
    attrs = ["residence", "libelle", "ville", "codePostal", "prix", "prix_min", "sorting_prix", "flap", "dateDispo", "nb_lots", "surface", "surface_min", "surface_max", "typeBien"]
    params_str = f"query=&hitsPerPage=1000&filters=neuf:1&attributesToRetrieve={json.dumps(attrs)}"
    
    payload = {
        "requests": [
            {
                "indexName": index_name,
                "params": params_str
            }
        ]
    }
    
    try:
        response = requests.post(url, params=params, json=payload, timeout=20)
        if response.status_code == 200:
            data = response.json()
            hits = data['results'][0]['hits']
            print(f"Successfully retrieved {len(hits)} hits!")
            
            programs = []
            for h in hits:
                # Extract clean fields
                name = h.get('libelle', h.get('residence', 'N/A'))
                city = h.get('ville', 'N/A')
                cp = h.get('codePostal', 'N/A')
                
                # Pricing Logic: prioritize prix_min and surface_min for consistency
                price = h.get('prix_min') or h.get('prix') or h.get('sorting_prix', 0)
                # Ensure price is valid
                if isinstance(price, (int, float)) and price <= 0:
                    price = h.get('sorting_prix', 0)
                
                surface = h.get('surface_min') or h.get('surface', 0)
                if not surface and h.get('surface'):
                    surface = h.get('surface')
                
                # Calculate Prix/m2
                prix_m2 = 0
                if price and surface and surface > 0:
                    prix_m2 = round(price / surface, 2)
                
                # Status Logic: Prioritize dateDispo
                status = h.get('flap', 'En cours')
                date_dispo = h.get('dateDispo')
                if isinstance(date_dispo, dict) and 'date' in date_dispo:
                    try:
                        # Date format: 2026-12-31 00:00:00.000000
                        dt_str = date_dispo['date'].split(' ')[0]
                        dt = datetime.strptime(dt_str, "%Y-%m-%d")
                        quarter = (dt.month - 1) // 3 + 1
                        q_name = f"{quarter}er" if quarter == 1 else f"{quarter}e"
                        status = f"{q_name} trim. {dt.year}"
                    except:
                        pass
                elif any(x in status.lower() for x in ["bien", "lot", "restant"]):
                    # If flap is "X biens restants", keep it but dateDispo is better
                    pass
                
                programs.append({
                    "Source": "Nexity",
                    "Type": h.get('typeBien', 'N/A'),
                    "Nom": name,
                    "Statut": status,
                    "Localisation": f"{city} ({cp})",
                    "Nb_Logements": h.get('nb_lots', 0),
                    "Prix_m2": prix_m2,
                    "Date_Scraping": datetime.now().strftime("%Y-%m-%d")
                })
            
            df = pd.DataFrame(programs)
            df.to_csv('data.csv', index=False, encoding='utf-8-sig')
            print(f"Saved {len(df)} programs to data.csv.")
            return True
    except Exception as e:
        print(f"Scraping Error: {e}")
        
    return False

if __name__ == "__main__":
    scrape_nexity()
