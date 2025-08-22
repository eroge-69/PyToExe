import xml.etree.ElementTree as ET
import re

def parse_mamemap(filename):
    """Parse mamemap.txt and return a dictionary with filename: full_name"""
    game_map = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and '";"' in line:
                parts = line.split('";"')
                if len(parts) >= 2:
                    filename = parts[0].replace('"', '').strip()
                    full_name = parts[1].replace('"', '').strip()
                    game_map[filename] = full_name
    return game_map

def update_gamelist(gamelist_file, mamemap_file, output_file):
    """Update gamelist.xml with information from mamemap.txt"""
    # Parse mamemap
    game_map = parse_mamemap(mamemap_file)
    
    # Parse gamelist.xml
    tree = ET.parse(gamelist_file)
    root = tree.getroot()
    
    for game in root.findall('game'):
        # Get filename from path
        path = game.find('path').text
        filename_match = re.search(r'\./(.*?)\.zip', path)
        
        if filename_match:
            filename = filename_match.group(1)
            
            # Check if we have mapping for this filename
            if filename in game_map:
                full_name = game_map[filename]
                gameid = game.find('gameid').text
                
                # Update language tags
                for lang_tag in ['zh_CN', 'en_US', 'zh_TW', 'ko_KR']:
                    tag = game.find(lang_tag)
                    if tag is not None:
                        tag.text = f"{gameid}  {full_name}"
                
                # Update name tag
                name_tag = game.find('name')
                if name_tag is not None:
                    name_tag.text = full_name
    
    # Save updated XML
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"Archivo actualizado guardado como: {output_file}")

# Usage
update_gamelist('gamelist.xml', 'mamemap.txt', 'gamelist_updated.xml')