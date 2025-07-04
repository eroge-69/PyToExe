# Hex to COE Converter for Xilinx BRAM
# Usage: python hex2coe.py input.hex output.coe

import sys

def hex_to_coe(input_hex, output_coe):
    with open(input_hex, 'r') as f:
        hex_lines = [line.strip() for line in f if line.strip()]
    
    with open(output_coe, 'w') as f:
        f.write("memory_initialization_radix=16;\n")
        f.write("memory_initialization_vector=\n")
        f.write(",\n".join(hex_lines) + ";")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python hex2coe.py input.hex output.coe")
        sys.exit(1)
    hex_to_coe(sys.argv[1], sys.argv[2])
    print(f"Converted {sys.argv[1]} to {sys.argv[2]}")
