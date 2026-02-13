import requests
import json

def verify_values():
    app_id = "04QRMGY2OL"
    api_key = "31bd735badd4f77d8e2dc769e29d8d04"
    index_name = "prod_bien"
    url = f"https://{app_id}-dsn.algolia.net/1/indexes/*/queries"
    params = {"x-algolia-api-key": api_key, "x-algolia-application-id": app_id}
    
    # Specific attributes
    attrs = ["residence", "libelle", "nb_lots", "surface", "surface_min", "prix", "sorting_prix"]
    payload = {
        "requests": [
            {
                "indexName": index_name,
                "params": f"query=&hitsPerPage=10&attributesToRetrieve={json.dumps(attrs)}"
            }
        ]
    }
    
    r = requests.post(url, params=params, json=payload)
    hits = r.json()['results'][0]['hits']
    
    for i, h in enumerate(hits):
        print(f"\nHit {i+1}: {h.get('residence') or h.get('libelle')}")
        print(f"  nb_lots: {h.get('nb_lots')}")
        print(f"  surface: {h.get('surface')}")
        print(f"  surface_min: {h.get('surface_min')}")
        print(f"  prix: {h.get('prix')}")

if __name__ == "__main__":
    verify_values()
