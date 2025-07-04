import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
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
            'cleanupradius': '1000',
            'deletable': '1',
            'init_random': '0',
            'remove_damaged': '0',
            'position': 'fixed',
            'limit': 'child',
            'active': '1'
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
    
    def create_event_definition(self, event_name):
        """Create the event definition XML element"""
        event = ET.Element('event', name=event_name)
        
        # Add standard parameters
        for param, value in self.default_event_params.items():
            if param in ['deletable', 'init_random', 'remove_damaged']:
                continue  # These go in flags
            elif param in ['position', 'limit', 'active']:
                elem = ET.SubElement(event, param)
                elem.text = value
            else:
                elem = ET.SubElement(event, param)
                elem.text = value
        
        # Add flags element
        flags = ET.SubElement(event, 'flags')
        flags.set('deletable', self.default_event_params['deletable'])
        flags.set('init_random', self.default_event_params['init_random'])
        flags.set('remove_damaged', self.default_event_params['remove_damaged'])
        
        # Add empty children element
        ET.SubElement(event, 'children')
        
        return event
    
    def create_spawn_definition(self, event_name, reference_obj, group_name):
        """Create the spawn definition XML element"""
        event = ET.Element('event', name=event_name)
        
        # Add zone element
        zone = ET.SubElement(event, 'zone')
        zone.set('smin', '0')
        zone.set('smax', '0')
        zone.set('dmin', '1')
        zone.set('dmax', '1')
        zone.set('r', '20')
        
        # Add pos element
        pos = ET.SubElement(event, 'pos')
        pos.set('x', str(reference_obj['pos'][0]))
        pos.set('z', str(reference_obj['pos'][2]))
        pos.set('a', str(reference_obj['ypr'][0]))
        pos.set('y', str(reference_obj['pos'][1]))
        pos.set('group', group_name)
        
        return event
    
    def create_group_definition(self, group_name, objects):
        """Create the group definition XML element"""
        group = ET.Element('group', name=group_name)
        
        reference_pos = objects[0]['pos']
        
        for i, obj in enumerate(objects):
            child = ET.SubElement(group, 'child')
            child.set('type', obj['name'])
            
            if i == 0:
                # First object is the reference point
                child.set('deloot', '0')
                child.set('lootmax', '3')
                child.set('lootmin', '1')
                child.set('x', '0')
                child.set('z', '0')
                child.set('a', '0')
                child.set('y', '0')
            else:
                # Calculate relative position
                rel_pos = self.calculate_relative_position(obj['pos'], reference_pos)
                child.set('spawnsecondary', 'false')
                child.set('x', str(rel_pos[0]))
                child.set('z', str(rel_pos[2]))
                child.set('a', str(obj['ypr'][0]))
                child.set('y', str(rel_pos[1]))
        
        return group
    
    def prettify_xml(self, elem):
        """Return a pretty-printed XML string"""
        rough_string = ET.tostring(elem, 'unicode')
        reparsed = minidom.parseString(rough_string)
        pretty = reparsed.toprettyxml(indent='\t')
        
        # Remove empty lines and fix formatting
        lines = [line for line in pretty.split('\n') if line.strip()]
        # Remove XML declaration
        if lines and lines[0].startswith('<?xml'):
            lines = lines[1:]
        
        return '\n'.join(lines)
    
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
        
        # Create XML elements
        event_def = self.create_event_definition(event_name)
        spawn_def = self.create_spawn_definition(event_name, reference_obj, group_name)
        group_def = self.create_group_definition(group_name, objects)
        
        # Combine into final XML
        xml_parts = []
        xml_parts.append('<!-- Event -->')
        xml_parts.append(self.prettify_xml(event_def))
        xml_parts.append('<!-- Spawn -->')
        xml_parts.append(self.prettify_xml(spawn_def))
        xml_parts.append('<!-- Group -->')
        xml_parts.append(self.prettify_xml(group_def))
        
        return '\n'.join(xml_parts)
    
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
    
    # Method 1: Try command line argument
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
        print("No valid JSON file found. Please ensure your JSON file is in the same directory.")
        print("Supported filenames: input.json, objects.json, dayz_objects.json")
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
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_converted.xml"
    except:
        output_file = "converted_output.xml"
    
    # Save XML file
    print(f"Saving XML file: {output_file}")
    if converter.save_xml(xml_content, output_file):
        print("✓ Conversion completed successfully!")
        print(f"Output saved to: {output_file}")
        print("\nXML Content:")
        print("-" * 50)
        print(xml_content)
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