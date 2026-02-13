import re

def search_fields():
    try:
        with open("debug_nexity.html", "r", encoding="utf-8") as f:
            content = f.read()
            
        fields = ['nb_lots', 'nbLots', 'surface', 'surface_min', 'surface_max', 'prix_m2', 'prixM2']
        for field in fields:
            pos = content.find(field)
            if pos != -1:
                print(f"\n--- Found '{field}' at {pos} ---")
                # Show context: is it in a list or a JSON?
                print(content[pos-100:pos+300])
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_fields()
