import requests
import json

def probe_counts():
    app_id = "04QRMGY2OL"
    api_key = "31bd735badd4f77d8e2dc769e29d8d04"
    index_name = "prod_bien"
    url = f"https://{app_id}-dsn.algolia.net/1/indexes/*/queries"
    params = {"x-algolia-api-key": api_key, "x-algolia-application-id": app_id}
    
    queries = [
        {"indexName": index_name, "params": "query=&hitsPerPage=0&filters=neuf:1"}, # All Neuf
        {"indexName": index_name, "params": "query=&hitsPerPage=0&filters=neuf:1 AND typeBien:Appartement"}, # Apartments
        {"indexName": index_name, "params": "query=&hitsPerPage=0&filters=neuf:1 AND typeBien:Maison"}, # Houses
        {"indexName": index_name, "params": "query=&hitsPerPage=0&facets=[\"typeBien\"]"} # Type breakdown
    ]
    
    payload = {"requests": queries}
    r = requests.post(url, params=params, json=payload)
    results = r.json()['results']
    
    print(f"Total Neuf (Algolia): {results[0]['nbHits']}")
    print(f"Appartements: {results[1]['nbHits']}")
    print(f"Maisons: {results[2]['nbHits']}")
    
    facets = results[3].get('facets', {}).get('typeBien', {})
    print(f"\nBreakdown by typeBien: {facets}")

if __name__ == "__main__":
    probe_counts()
