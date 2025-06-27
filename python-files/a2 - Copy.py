import os
import re
import csv

# Automatically get the folder the script is in
folder_path = os.path.dirname(os.path.abspath(sys.argv[0]))

# Dictionary to hold the results
depth_results = {}

# Regex patterns
date_pattern = re.compile(r'Date = (.+)')
bottle_pattern = re.compile(r'Bottle (\d+)')
depth_pattern = re.compile(r'DepSM\s*=\s*([0-9.]+)')

# Process each .btl file in the folder
for filename in os.listdir(folder_path):
	if filename.endswith(".btl"):
		file_path = os.path.join(folder_path, filename)
		with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
			date = "Unknown"
			bottle_num = "Unknown"
			for line in file:
				date_match = date_pattern.search(line)
				if date_match:
					date = date_match.group(1).strip()

				bottle_match = bottle_pattern.search(line)
				if bottle_match:
					bottle_num = bottle_match.group(1).strip()

				depth_match = depth_pattern.search(line)
				if depth_match:
					depth = float(depth_match.group(1))
					# Create a unique key combining filename and bottle
					key = f"{filename}_bottle_{bottle_num}"
					depth_results[key] = {
						"date": date,
						"file": filename,
						"bottle": bottle_num,
						"depth_m": depth
					}

# Export to CSV
output_csv = os.path.join(folder_path, "bottle_depths_output.csv")
with open(output_csv, 'w', newline='') as csvfile:
	fieldnames = ['date', 'filename', 'bottle', 'depth_m']
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()
	for data in depth_results.values():
		writer.writerow({
			'date': data['date'],
			'filename': data['file'],
			'bottle': data['bottle'],
			'depth_m': data['depth_m']
		})

print(f"✅ Bottle depth data saved to: {output_csv}")
input("\nPress Enter to exit...")
