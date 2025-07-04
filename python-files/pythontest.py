import json
import sys

def convert_dayz_json_to_xml(json_file_path):
    """Convert DayZ JSON to XML format"""
    
    # Load JSON file
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
    except:
        print("Error: Could not read JSON file")
        return None
    
    # Get objects array
    if 'Objects' not in data:
        print("Error: No 'Objects' found in JSON")
        return None
    
    objects = data['Objects']
    if not objects:
        print("Error: Objects array is empty")
        return None
    
    # Get reference object (first one)
    ref_obj = objects[0]
    ref_pos = ref_obj['pos']
    base_name = ref_obj['name']
    
    # Generate names
    event_name = f"Static_{base_name}"
    group_name = f"Injector_{base_name}"
    
    # Build XML string
    xml = ""
    
    # Event section
    xml += "<!-- Event -->\n"
    xml += f'<event name="{event_name}">\n'
    xml += "\t<nominal>1</nominal>\n"
    xml += "\t<min>0</min>\n"
    xml += "\t<max>0</max>\n"
    xml += "\t<lifetime>1800</lifetime>\n"
    xml += "\t<restock>0</restock>\n"
    xml += "\t<saferadius>1000</saferadius>\n"
    xml += "\t<distanceradius>1000</distanceradius>\n"
    xml += "\t<cleanupradius>1000</cleanupradius>\n"
    xml += "\t<!-- <secondary>InfectedArmy</secondary> -->\n"
    xml += '\t<flags deletable="1" init_random="0" remove_damaged="0"/>\n'
    xml += "\t<position>fixed</position>\n"
    xml += "\t<limit>child</limit>\n"
    xml += "\t<active>1</active>\n"
    xml += "\t<children/>\n"
    xml += "</event>\n"
    
    # Spawn section
    xml += "<!-- Spawn -->\n"
    xml += f'<event name="{event_name}">\n'
    xml += '\t<zone smin="0" smax="0" dmin="1" dmax="1" r="20" />\n'
    xml += f'\t<pos x="{ref_pos[0]}" z="{ref_pos[2]}" a="{ref_obj["ypr"][0]}" y="{ref_pos[1]}" group="{group_name}"/>\n'
    xml += "</event>\n"
    
    # Group section
    xml += "<!-- Group -->\n"
    xml += f'<group name="{group_name}">\n'
    
    # Add each object as child
    for i, obj in enumerate(objects):
        obj_pos = obj['pos']
        obj_name = obj['name']
        obj_ypr = obj['ypr'][0]
        
        if i == 0:
            # First object (reference point)
            xml += f'\t<child type="{obj_name}" deloot="0" lootmax="3" lootmin="1" x="0" z="0" a="0" y="0"/>\n'
        else:
            # Calculate relative position
            rel_x = obj_pos[0] - ref_pos[0]
            rel_y = obj_pos[1] - ref_pos[1]
            rel_z = obj_pos[2] - ref_pos[2]
            xml += f'\t<child type="{obj_name}" spawnsecondary="false" x="{rel_x}" z="{rel_z}" a="{obj_ypr}" y="{rel_y}"/>\n'
    
    xml += "</group>"
    
    return xml

def main():
    print("DayZ JSON to XML Converter")
    print("=" * 30)
    
    # Get input file
    input_file = None
    
    # Check if file was dragged onto exe
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        print(f"Processing: {input_file}")
    else:
        # Ask for file path
        input_file = input("Enter JSON file path: ").strip().strip('"')
    
    if not input_file:
        print("No file provided")
        input("Press Enter to exit...")
        return
    
    # Convert
    print("Converting...")
    xml_result = convert_dayz_json_to_xml(input_file)
    
    if xml_result is None:
        print("Conversion failed")
        input("Press Enter to exit...")
        return
    
    # Save result
    output_file = input_file.replace('.json', '_converted.xml')
    
    try:
        with open(output_file, 'w') as f:
            f.write(xml_result)
        print(f"SUCCESS: Saved to {output_file}")
    except:
        print("Could not save file. Here's the XML:")
        print("-" * 40)
        print(xml_result)
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()