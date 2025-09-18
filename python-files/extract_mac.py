import re
import sys

def extract_macs(input_path, output_path):
    # Read file content
    with open(input_path, "r", encoding="utf-8") as infile:
        content = infile.read()

    # Extract all MAC addresses
    macs = re.findall(r"MAC\s*=\s*([0-9A-F:]+)", content)

    # Save extracted MACs to new file
    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write("\n".join(macs))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: extract_mac.exe input.txt output.txt")
    else:
        extract_macs(sys.argv[1], sys.argv[2])
        print(f"MACs saved to {sys.argv[2]}")
