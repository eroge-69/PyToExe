#!/usr/bin/env python3
import argparse
import sys

def hex_to_ascii(hex_string):
    """
    Convert a hexadecimal string to ASCII text.
    
    Args:
        hex_string (str): Hexadecimal string to convert
        
    Returns:
        str: ASCII representation of the hex string
        
    Raises:
        ValueError: If the hex string is invalid
    """
    # Remove any whitespace and convert to lowercase
    hex_string = hex_string.replace(" ", "").replace("\n", "").replace("\t", "").lower()
    
    # Remove '0x' prefix if present
    if hex_string.startswith('0x'):
        hex_string = hex_string[2:]
    
    # Check if string length is even (each ASCII char needs 2 hex digits)
    if len(hex_string) % 2 != 0:
        raise ValueError("Hex string must have an even number of characters")
    
    # Check if all characters are valid hex digits
    if not all(c in '0123456789abcdef' for c in hex_string):
        raise ValueError("Invalid hex characters found")
    
    # Convert hex pairs to ASCII characters
    ascii_chars = []
    for i in range(0, len(hex_string), 2):
        hex_pair = hex_string[i:i+2]
        ascii_value = int(hex_pair, 16)
        
        # Check if it's a printable ASCII character
        if 32 <= ascii_value <= 126:
            ascii_chars.append(chr(ascii_value))
        else:
            # For non-printable characters, show them as [XX] where XX is the hex value
            ascii_chars.append(f'[{hex_pair.upper()}]')
    
    return ''.join(ascii_chars)

def main():
    parser = argparse.ArgumentParser(
        description='Convert hexadecimal string to ASCII text',
        epilog='Example: %(prog)s "48656c6c6f20576f726c64" or %(prog)s "0x48656c6c6f"'
    )
    
    parser.add_argument(
        'hex_string',
        help='Hexadecimal string to convert (with or without 0x prefix)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed conversion information'
    )
    
    parser.add_argument(
        '--raw',
        action='store_true',
        help='Output only printable ASCII characters, skip non-printable ones'
    )
    
    args = parser.parse_args()
    
    try:
        if args.verbose:
            print(f"Input hex string: {args.hex_string}")
            print(f"Cleaned hex string: {args.hex_string.replace(' ', '').replace('0x', '').lower()}")
        
        ascii_result = hex_to_ascii(args.hex_string)
        
        if args.raw:
            # Filter out non-printable character markers [XX]
            import re
            ascii_result = re.sub(r'\[[0-9A-F]{2}\]', '', ascii_result)
        
        if args.verbose:
            print(f"ASCII result: {ascii_result}")
        else:
            print(ascii_result)
            
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()