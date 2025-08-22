import os
import glob

def main():
    # Global ID counter
    id_counter = 1
    
    # Fixed list of folders in order
    folders = [
        "mame", "arcade", "cps1", "cps2", "cps3", "fbneo", "n64", "psp",
        "atari5200", "atari7800", "dreamcast", "genh", "mastersystem", "ngp",
        "pcenginecd", "wonderswan", "wonderswancolor", "gbah", "snes", "atari2600",
        "atarilynx", "gamegear", "gb", "gba", "gbc", "genesis", "megadrive",
        "nes", "nesh", "ngpc", "pcengine", "psx", "sfc"
    ]

    print("==============================================")
    print("  GameList XML Generator v0.132  -  By Osini Mendoza")
    print("==============================================")
    print()

    # Process each folder
    for folder in folders:
        if os.path.exists(folder) and os.path.isdir(folder):
            print(f"Processing folder: {folder}")
            files_found = 0
            
            # Get list of files in directory, excluding certain extensions
            excluded_extensions = {'.xml', '.exe', '.flash', '.nv', '.txt', '.fs', '.srm'}
            files = []
            
            try:
                for file in os.listdir(folder):
                    if os.path.isfile(os.path.join(folder, file)):
                        file_ext = os.path.splitext(file)[1].lower()
                        if file_ext not in excluded_extensions:
                            files.append(file)
                            files_found += 1
            except PermissionError:
                print(f"   Permission denied accessing folder: {folder}")
                continue
            
            if files_found > 0:
                xml_content = []
                xml_content.append('<?xml version="1.0" encoding="UTF-8"?>')
                xml_content.append('<gameList>')
                
                for file in files:
                    romname = os.path.splitext(file)[0]
                    romext = os.path.splitext(file)[1]
                    
                    xml_content.append('  <game>')
                    xml_content.append(f'    <gameid>{id_counter}</gameid>')
                    xml_content.append(f'    <path>./{romname}{romext}</path>')
                    xml_content.append(f'    <image>./images/{romname}.png</image>')
                    xml_content.append('    <video_id>0</video_id>')
                    xml_content.append('    <class_type>0</class_type>')
                    xml_content.append('    <game_type>0</game_type>')
                    xml_content.append(f'    <timer>{folder}</timer>')
                    xml_content.append(f'    <zh_CN>{id_counter}  {romname}</zh_CN>')
                    xml_content.append(f'    <en_US>{id_counter}  {romname}</en_US>')
                    xml_content.append(f'    <zh_TW>{id_counter}  {romname}</zh_TW>')
                    xml_content.append(f'    <ko_KR>{id_counter}  {romname}</ko_KR>')
                    xml_content.append(f'    <name>{romname}</name>')
                    xml_content.append('  </game>')
                    
                    id_counter += 1
                
                xml_content.append('</gameList>')
                
                # Write to gamelist.xml in the current folder
                output_file = os.path.join(folder, "gamelist.xml")
                try:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(xml_content))
                    print(f"   Files processed in {folder}: {files_found}")
                except IOError as e:
                    print(f"   Error writing file {output_file}: {e}")
            
            else:
                print(f"   No files found in {folder}")
                
        else:
            print(f"Folder not found: {folder}")

    print("==============================================")
    print(f"Process completed. Last ID assigned: {id_counter}")
    input("Press Enter to continue...")

if __name__ == "__main__":
    main()