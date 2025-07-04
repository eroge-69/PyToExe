import json
import os
import sys

class DayZConverter:
    def __init__(self):
        self.default_event_params = {
            'nominal': '1',
            'min': '0',
            'max': '0',
            'lifetime': '1800',
            'restock': '0',
            'saferadius': '1000',
            'distanceradius': '1000',
            'cleanupradius': '1000'
        }
    
    def load_json(self, file_path):
        """Load JSON data from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return None
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format - {e}")
            return None
    
    def generate_event_name(self, base_name):
        """Generate event name with Static_ prefix"""
        return f"Static_{base_name}"
    
    def generate_group_name(self, base_name):
        """Generate group name with Injector_ prefix"""
        return f"Injector_{base_name}"
    
    def calculate_relative_position(self, obj_pos, reference_pos):
        """Calculate relative position from reference point"""
        return [
            obj_pos[0] - reference_pos[0],  # x
            obj_pos[1] - reference_pos[1],  # y
            obj_pos[2] - reference_pos[2]   # z
        ]
    
    def create_event_xml(self, event_name):
        """Create the event definition XML as string"""
        xml = f'<event name="{event_name}">\n'
        xml += f'\t<nominal>{self.default_event_params["nominal"]}</nominal>\n'
        xml += f'\t<min>{self.default_event_params["min"]}</min>\n'
        xml += f'\t<max>{self.default_event_params["max"]}</max>\n'
        xml += f'\t<lifetime>{self.default_event_params["lifetime"]}</lifetime>\n'
        xml += f'\t<restock>{self.default_event_params["restock"]}</restock>\n'
        xml += f'\t<saferadius>{self.default_event_params["saferadius"]}</saferadius>\n'
        xml += f'\t<distanceradius>{self.default_event_params["distanceradius"]}</distanceradius>\n'
        xml += f'\t<cleanupradius>{self.default_event_params["cleanupradius"]}</cleanupradius>\n'
        xml += '\t<!-- <secondary>InfectedArmy</secondary> -->\n'
        xml += '\t<flags deletable="1" init_random="0" remove_damaged="0"/>\n'
        xml += '\t<position>fixed</position>\n'
        xml += '\t<limit>child</limit>\n'
        xml += '\t<active>1</active>\n'
        xml += '\t<children/>\n'
        xml += '</event>'
        return xml
    
    def create_spawn_xml(self, event_name, reference_obj, group_name):
        """Create the spawn definition XML as string"""
        xml = f'<event name="{event_name}">\n'
        xml += '\t<zone smin="0" smax="0" dmin="1" dmax="1" r="20" />\n'
        xml += f'\t<pos x="{reference_obj["pos"][0]}" z="{reference_obj["pos"][2]}" a="{reference_obj["ypr"][0]}" y="{reference_obj["pos"][1]}" group="{group_name}"/>\n'
        xml += '</event>'
        return xml
    
    def create_group_xml(self, group_name, objects):
        """Create the group definition XML as string"""
        xml = f'<group name="{group_name}">\n'
        
        reference_pos = objects[0]['pos']
        
        for i, obj in enumerate(objects):
            if i == 0:
                # First object is the reference point
                xml += f'\t<child type="{obj["name"]}" deloot="0" lootmax="3" lootmin="1" x="0" z="0" a="0" y="0"/>\n'
            else:
                # Calculate relative position
                rel_pos = self.calculate_relative_position(obj['pos'], reference_pos)
                xml += f'\t<child type="{obj["name"]}" spawnsecondary="false" x="{rel_pos[0]}" z="{rel_pos[2]}" a="{obj["ypr"][0]}" y="{rel_pos[1]}"/>\n'
        
        xml += '</group>'
        return xml
    
    def convert_json_to_xml(self, json_data):
        """Main conversion function"""
        if not json_data or 'Objects' not in json_data:
            print("Error: Invalid JSON structure. Expected 'Objects' array.")
            return None
        
        objects = json_data['Objects']
        if not objects:
            print("Error: No objects found in JSON.")
            return None
        
        # Get the first object as reference
        reference_obj = objects[0]
        base_name = reference_obj['name']
        
        # Generate names
        event_name = self.generate_event_name(base_name)
        group_name = self.generate_group_name(base_name)
        
        # Create XML sections
        event_xml = self.create_event_xml(event_name)
        spawn_xml = self.create_spawn_xml(event_name, reference_obj, group_name)
        group_xml = self.create_group_xml(group_name, objects)
        
        # Combine into final XML
        final_xml = "<!-- Event -->\n"
        final_xml += event_xml + "\n"
        final_xml += "<!-- Spawn -->\n"
        final_xml += spawn_xml + "\n"
        final_xml += "<!-- Group -->\n"
        final_xml += group_xml
        
        return final_xml
    
    def save_xml(self, xml_content, output_path):
        """Save XML content to file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            return True
        except Exception as e:
            print(f"Error saving XML file: {e}")
            return False

def main():
    converter = DayZConverter()
    
    print("DayZ JSON to XML Converter")
    print("=" * 30)
    
    # Try multiple input methods for compatibility
    json_data = None
    input_file = None
    
    # Method 1: Try command line argument (drag & drop)
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        print(f"Loading JSON file: {input_file}")
        json_data = converter.load_json(input_file)
    
    # Method 2: Try interactive input
    if json_data is None:
        try:
            input_file = input("Enter JSON file path (or drag & drop): ").strip().strip('"')
            if input_file:
                print(f"Loading JSON file: {input_file}")
                json_data = converter.load_json(input_file)
        except:
            print("Interactive input not supported in this environment.")
    
    # Method 3: Fallback - look for default files
    if json_data is None:
        default_files = ['input.json', 'objects.json', 'dayz_objects.json']
        for filename in default_files:
            if os.path.exists(filename):
                print(f"Found default file: {filename}")
                json_data = converter.load_json(filename)
                input_file = filename
                break
    
    if json_data is None:
        print("No valid JSON file found.")
        print("Usage: Drag your JSON file onto this .exe")
        print("Or place your JSON file in the same directory with name: input.json")
        try:
            input("Press Enter to exit...")
        except:
            pass
        return
    
    # Convert to XML
    print("Converting JSON to XML...")
    xml_content = converter.convert_json_to_xml(json_data)
    
    if xml_content is None:
        try:
            input("Press Enter to exit...")
        except:
            pass
        return
    
    # Generate output file path
    try:
        if input_file:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_converted.xml"
        else:
            output_file = "converted_output.xml"
    except:
        output_file = "converted_output.xml"
    
    # Save XML file
    print(f"Saving XML file: {output_file}")
    if converter.save_xml(xml_content, output_file):
        print("✓ Conversion completed successfully!")
        print(f"Output saved to: {output_file}")
    else:
        print("✗ Failed to save XML file.")
        print("Here's the converted XML content:")
        print("-" * 50)
        print(xml_content)
    
    try:
        input("Press Enter to exit...")
    except:
        pass

if __name__ == "__main__":
    main()