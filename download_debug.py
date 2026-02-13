
import requests
import sys

def download(url, output_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(r.text)
        print(f"Downloaded {url} to {output_path}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python download_debug.py <url> <output_path>")
        sys.exit(1)
    download(sys.argv[1], sys.argv[2])
