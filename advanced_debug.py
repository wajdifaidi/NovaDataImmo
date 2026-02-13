import requests
import json
import time

def bypass_test():
    url = "https://www.nexity.fr/annonces-immobilieres/achat-vente/appartement/neuf/france"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        print(f"Attempting to fetch {url}...")
        response = session.get(url, timeout=20)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Success! Analysing content...")
            with open("debug_nexity.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            
            if "__NEXT_DATA__" in response.text:
                print("Found __NEXT_DATA__ JSON block!")
                # Rough extraction
                start = response.text.find("__NEXT_DATA__") + 14
                end = response.text.find("</script>", start)
                json_str = response.text[start:end].strip()
                # Remove potential tail
                if json_str.endswith(";"): json_str = json_str[:-1]
                
                try:
                    data = json.loads(json_str)
                    # Check for programs in the JSON
                    # Usually under props.pageProps.initialState...
                    print("JSON loaded successfully.")
                    # Let's save a snippet to analyze structure
                    with open("debug_data.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                    print("Saved debug_data.json for analysis.")
                except Exception as e:
                    print(f"Failed to parse JSON: {e}")
            else:
                print("No __NEXT_DATA__ found. Site might be using a different architecture.")
        else:
            print(f"Failed with status {response.status_code}")
            print(f"Body snippet: {response.text[:200]}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    bypass_test()
