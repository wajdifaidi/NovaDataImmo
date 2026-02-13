
import json
import sys

def find_value_in_nuxt(file_path, target_value):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    indices = []
    for i, val in enumerate(data):
        if isinstance(val, str) and target_value.lower() in val.lower():
            indices.append(i)
            # Use sys.stdout.buffer.write for reliable encoding-independent output
            msg = f"Found '{target_value}' at index {i}\n"
            sys.stdout.buffer.write(msg.encode('utf-8'))
    
    if not indices:
        msg = f"Value '{target_value}' not found.\n"
        sys.stdout.buffer.write(msg.encode('utf-8'))
        return

    # Now find who points to these indices
    for idx in indices:
        msg = f"\n--- Searching for references to index {idx} ---\n"
        sys.stdout.buffer.write(msg.encode('utf-8'))
        for i, val in enumerate(data):
            if isinstance(val, dict):
                for k, v in val.items():
                    if v == idx:
                        msg = f"Index {i} (dict) has key '{k}' pointing to {idx}\n"
                        sys.stdout.buffer.write(msg.encode('utf-8'))
            elif isinstance(val, list):
                if idx in val:
                    msg = f"Index {i} (list) contains index {idx}\n"
                    sys.stdout.buffer.write(msg.encode('utf-8'))

if __name__ == "__main__":
    file_path = sys.argv[1]
    target_value = sys.argv[2]
    find_value_in_nuxt(file_path, target_value)
