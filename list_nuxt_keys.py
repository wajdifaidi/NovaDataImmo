
import json
import sys

def list_nuxt_keys_deep(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list) and len(data) > 3:
        # data[1] has the keys for the main object
        # In Bordeaux, data[3] had the 'search-products' etc.
        data_keys_obj_idx = data[1].get('data')
        if data_keys_obj_idx is not None:
            # data[data_keys_obj_idx] is ['ShallowReactive', NEXT_IDX]
            next_idx = data[data_keys_obj_idx][1]
            data_keys_obj = data[next_idx]
            print(f"Keys in data (at index {next_idx}):")
            for k in data_keys_obj.keys():
                val_idx = data_keys_obj[k]
                print(f"- {k} (index {val_idx})")
                if isinstance(val_idx, int) and val_idx < len(data):
                    print(f"  Preview: {str(data[val_idx])[:150]}...")
    else:
        print("Unexpected data structure or data too small")

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else 'nuxt_data.json'
    list_nuxt_keys_deep(file_path)
