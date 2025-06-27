import os
import re

# Use raw string for full Windows path
folder_path = r'C:\Users\carla\OneDrive - Dalhousie University\CERC Ocean\Projects\Bedford Basin Planetary\Data\65 - May 29 2025 (Bi-Weekly 16)\CTD Rosette'

depth_results = {}

# Regex to match bottle header lines
bottle_line_pattern = re.compile(r'^\s*(\d+)\s+(\w+ \d+ \d{4})\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)')

# List all files ending with .btl
btl_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.btl')]

if not btl_files:
    print("No .btl files found in the directory.")

# Process each .btl file
for filename in btl_files:
    filepath = os.path.join(folder_path, filename)
    print(f"Processing: {filename}")
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as file:
            for line in file:
                match = bottle_line_pattern.match(line)
                if match:
                    bottle_num = int(match.group(1))
                    date = match.group(2)
                    depth = float(match.group(4))  # DepSM column
                    key = f"{filename}_bottle_{bottle_num}"
                    depth_results[key] = {
                        "date": date,
                        "depth_m": depth,
                        "file": filename
                    }
    except Exception as e:
        print(f"Error reading {filename}: {e}")

# Output summary
print("\nExtracted Depths:")
for key, data in sorted(depth_results.items()):
    print(f"{key}: {data['depth_m']} m on {data['date']} (from {data['file']})")
