import requests
import json

def probe_refined():
    app_id = "04QRMGY2OL"
    api_key = "31bd735badd4f77d8e2dc769e29d8d04"
    index_name = "prod_bien"
    url = f"https://{app_id}-dsn.algolia.net/1/indexes/*/queries"
    params = {"x-algolia-api-key": api_key, "x-algolia-application-id": app_id}
    
    # Query all neuf:1 and get facet breakdown
    query = {
        "indexName": index_name, 
        "params": "query=&hitsPerPage=0&filters=neuf:1&facets=[\"typeBien\"]"
    }
    
    payload = {"requests": [query]}
    r = requests.post(url, params=params, json=payload)
    results = r.json()['results'][0]
    
    print(f"Total Neuf (Algolia): {results['nbHits']}")
    facets = results.get('facets', {}).get('typeBien', {})
    print(f"Breakdown: {facets}")

if __name__ == "__main__":
    probe_refined()
