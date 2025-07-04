#!/usr/bin/env python
import sys

def hex_to_coe(hex_file, coe_file):
    # Header for COE file
    header = """memory_initialization_radix=16;
memory_initialization_vector=\n"""

    try:
        with open(hex_file, 'r') as f_hex:
            lines = f_hex.readlines()

        with open(coe_file, 'w') as f_coe:
            f_coe.write(header)

            # Write each line from .hex to .coe
            for line in lines:
                # Remove newline characters and add comma
                f_coe.write(line.strip() + ",\n")

            # Add trailing semicolon to complete COE format
            f_coe.write(";")

        print(f"Conversion successful: {hex_file} -> {coe_file}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python hex_to_coe.py <input.hex> <output.coe>")
        sys.exit(1)

    input_hex = sys.argv[1]
    output_coe = sys.argv[2]

    hex_to_coe(input_hex, output_coe)