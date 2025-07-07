#!/usr/bin/env python3
import sys
import argparse
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Union

VERSION = "1.0"

def main():
    parser = argparse.ArgumentParser(description=f"YMLMerge version {VERSION}")
    parser.add_argument('src', help='Source YML file')
    parser.add_argument('dest', help='Destination YML file')
    parser.add_argument('input_path', help='Dot notation path to the element to merge (e.g. "parent.child" or "parent.child@attribute")')
    parser.add_argument('--attr-match', nargs='*', default=[], 
                       help='List of attributes to use when matching multiple elements (e.g. "name id")')
    
    args = parser.parse_args()
    
    try:
        # Load source and destination files
        src_data = load_yml(args.src)
        dest_data = load_yml(args.dest)
        
        # Determine if we're merging an attribute or a node
        path_parts = args.input_path.split('@')
        is_attribute = len(path_parts) > 1
        
        if is_attribute:
            node_path = path_parts[0]
            attr_name = path_parts[1]
            print(f"Requested merge of attribute '{attr_name}' belonging to node '{node_path}'")
        else:
            node_path = args.input_path
            attr_name = None
            print(f"Requested merge of node '{node_path}'")
        
        # Perform the merge
        result = do_merge(src_data, dest_data, node_path, attr_name, args.attr_match)
        
        if result is None:
            print("No matching nodes found in source file. Nothing to merge.")
            return 1
        
        # Save the result
        save_yml(args.dest, dest_data)
        print("Merge successful")
        return 0
        
    except Exception as e:
        print(f"Exception caught: {str(e)}", file=sys.stderr)
        return 2

def load_yml(file_path: str) -> Dict:
    """Load a YML file and return its contents as a dictionary."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f) or {}

def save_yml(file_path: str, data: Dict):
    """Save a dictionary to a YML file."""
    with open(file_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

def get_node(data: Dict, path: str) -> Union[Dict, List, None]:
    """Get a node from a nested dictionary using dot notation."""
    if not path:
        return data
    
    parts = path.split('.')
    current = data
    
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list):
            try:
                index = int(part)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            except ValueError:
                return None
        else:
            return None
        
        if current is None:
            return None
    
    return current

def set_node(data: Dict, path: str, value: Union[Dict, List]):
    """Set a node in a nested dictionary using dot notation."""
    if not path:
        return
    
    parts = path.split('.')
    current = data
    
    for i, part in enumerate(parts[:-1]):
        if part not in current:
            current[part] = {}
        current = current[part]
        if not isinstance(current, dict):
            # Convert to dict if needed
            current = current[part] = {}
    
    current[parts[-1]] = value

def do_merge(
    src_data: Dict, 
    dest_data: Dict, 
    node_path: str, 
    attr_name: Optional[str] = None, 
    attr_match: List[str] = []
) -> bool:
    """
    Merge nodes or attributes from source YML to destination YML.
    
    Returns:
        True if merge was performed, False if nothing to merge
    """
    # Get the source node(s) to merge
    src_node = get_node(src_data, node_path)
    
    if src_node is None:
        return False
    
    if isinstance(src_node, list):
        # Handle merging of lists
        if not attr_match:
            raise ValueError("Attribute match list required when merging multiple list items")
        
        dest_node = get_node(dest_data, node_path)
        if dest_node is None:
            # Create the node if it doesn't exist
            set_node(dest_data, node_path, [])
            dest_node = get_node(dest_data, node_path)
        
        if not isinstance(dest_node, list):
            raise ValueError(f"Destination node {node_path} is not a list")
        
        # Merge each item from source to destination
        for src_item in src_node:
            if not isinstance(src_item, dict):
                raise ValueError("Can only merge dict items when using attribute matching")
            
            # Find matching item in destination
            matched = False
            for dest_item in dest_node:
                if isinstance(dest_item, dict):
                    # Check if all matching attributes match
                    match = all(
                        src_item.get(attr) == dest_item.get(attr)
                        for attr in attr_match
                        if attr in src_item
                    )
                    
                    if match:
                        # Merge the matching items
                        if attr_name:
                            # Merge specific attribute
                            if attr_name in src_item:
                                dest_item[attr_name] = src_item[attr_name]
                        else:
                            # Merge entire node
                            dest_item.update(src_item)
                        matched = True
                        break
            
            if not matched:
                # Add new item if no match found
                dest_node.append(src_item.copy())
        
        return True
    
    elif attr_name:
        # Handle attribute merge
        if not isinstance(src_node, dict):
            raise ValueError(f"Source node {node_path} is not a dictionary (cannot have attributes)")
        
        if attr_name not in src_node:
            return False
        
        dest_node = get_node(dest_data, node_path)
        if dest_node is None:
            # Create the node if it doesn't exist
            parent_path = '.'.join(node_path.split('.')[:-1])
            parent = get_node(dest_data, parent_path)
            if parent is None:
                raise ValueError(f"Parent node {parent_path} not found in destination")
            
            if isinstance(parent, dict):
                parent[node_path.split('.')[-1]] = {}
                dest_node = get_node(dest_data, node_path)
            else:
                raise ValueError(f"Parent node {parent_path} is not a dictionary")
        
        if not isinstance(dest_node, dict):
            raise ValueError(f"Destination node {node_path} is not a dictionary")
        
        # Merge the attribute
        dest_node[attr_name] = src_node[attr_name]
        return True
    
    else:
        # Handle node merge
        dest_node = get_node(dest_data, node_path)
        if dest_node is None:
            # Node doesn't exist - create it
            set_node(dest_data, node_path, src_node.copy() if isinstance(src_node, dict) else src_node)
            return True
        
        if isinstance(src_node, dict) and isinstance(dest_node, dict):
            # Merge dictionaries recursively
            for key, value in src_node.items():
                if key in dest_node and isinstance(value, dict) and isinstance(dest_node[key], dict):
                    # Recursive merge for nested dictionaries
                    do_merge(src_node, dest_node, key)
                else:
                    # Overwrite other values
                    dest_node[key] = value.copy() if hasattr(value, 'copy') else value
            return True
        else:
            # Replace non-dict values
            set_node(dest_data, node_path, src_node.copy() if hasattr(src_node, 'copy') else src_node)
            return True

if __name__ == '__main__':
    sys.exit(main())