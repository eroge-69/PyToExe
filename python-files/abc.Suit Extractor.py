import os
import sys
import zipfile
import re
from pathlib import Path

def extract_suit(file_path):
    """Extracts a .suit file as if it were a zip archive."""
    extract_path = Path(file_path).with_suffix('')
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    return extract_path

def find_asset_archive(root_dir):
    """Finds id.txt and retrieves the asset archive name."""
    for dirpath, _, filenames in os.walk(root_dir):
        if 'id.txt' in filenames:
            with open(os.path.join(dirpath, 'id.txt'), 'r') as f:
                archive_name = f.read().strip()
            archive_path = os.path.join(dirpath, archive_name)
            if os.path.exists(archive_path):
                return archive_path, dirpath
    return None, None

def split_asset_archive(file_path, output_dir):
    """Splits an asset archive into separate files based on '1TAD' markers."""
    file_types = {
        b'Config Built File': 'config.config',
        b'Texture Built File': 'texture.texture',
        b'Material Built File': 'material.material',
        b'Material Template Built File': 'materialgraph.materialgraph',
        b'Model Built File': 'model.model',
    }
    
    os.makedirs(output_dir, exist_ok=True)
    
    with open(file_path, 'rb') as f:
        data = f.read()
    
    positions = [m.start() - 36 for m in re.finditer(b'1TAD', data)]
    
    if not positions:
        print("No files found in asset archive.")
        return
    
    file_counters = {}
    
    for i, start in enumerate(positions):
        end = positions[i + 1] if i + 1 < len(positions) else len(data)
        file_data = data[start:end]
        
        # Identify file type
        file_type = None
        for key, ext in file_types.items():
            if key in file_data:
                file_type = ext
                break
        
        # Default numbering if no type found
        if not file_type:
            file_type = str(i)
        
        # Handle duplicate names
        base_name = file_type
        count = file_counters.get(file_type, 0)
        file_name = f"{base_name}" if count == 0 else f"{base_name.replace('.', str(count) + '.')}"
        file_counters[file_type] = count + 1
        
        # Save file
        with open(os.path.join(output_dir, file_name), 'wb') as out_file:
            out_file.write(file_data)
        
        print(f"Extracted: {file_name}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_suit_or_asset_archive>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    if input_path.endswith('.suit'):
        extracted_path = extract_suit(input_path)
        archive_path, archive_dir = find_asset_archive(extracted_path)
        if not archive_path:
            print("Asset archive not found in extracted .suit contents.")
            sys.exit(1)
        output_dir = os.path.join(archive_dir, 'assets')
    else:
        archive_path = input_path
        output_dir = os.path.join(os.path.dirname(input_path), 'assets')
    
    split_asset_archive(archive_path, output_dir)

title = "Asset Archive Extractor"
if __name__ == "__main__":
    print(title.center(50, '='))
    main()
