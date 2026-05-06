import json
import os

def update_data_js(json_path='resistors_compact.json', output_js='data.js'):
    """
    Specifically updates data.js from the compact JSON file.
    This is intended for incremental data updates without rewriting index.html.
    """
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(output_js, 'w', encoding='utf-8') as f:
        f.write(f"const DATA = {json.dumps(data, indent=None)};\n")
    
    print(f"Successfully updated {output_js} from {json_path}")

if __name__ == "__main__":
    update_data_js()
