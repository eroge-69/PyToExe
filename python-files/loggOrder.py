import re
import os
from collections import defaultdict

# Define the folder path containing the .scl files
folder_path = "."  # Current directory; change this to your specific directory if needed
output_file_path = "results.txt"

# Define the custom order for log levels
log_level_order = ["Fatal", "Error", "Warning", "Info", "Trace"]

# Initialize a list to hold all results
all_results = []

# Iterate over all .scl files in the specified folder
for filename in os.listdir(folder_path):
    if filename.endswith(".scl"):
        log_levels = defaultdict(list)  # Reset for each file
        
        with open(os.path.join(folder_path, filename), 'r') as file:
            lines = file.readlines()
            
            # Loop through lines to find "I_LOG_LEVEL :="
            for i in range(len(lines) - 1):  # Avoid index out of range
                if "I_LOG_LEVEL :=" in lines[i]:
                    # Extract the log level using regex
                    match = re.search(r'I_LOG_LEVEL\s*:=\s*["\']?(.*?)["\']?\s*$', lines[i])
                    if match:
                        log_level = match.group(1).split("_")[-1][:-2].capitalize()  # Remove the last two characters
                        
                        # Check the next line for "I_DESCRIPTION :="
                        if "I_DESCRIPTION :=" in lines[i + 1]:
                            # Extract the description
                            description = lines[i + 1].split("I_DESCRIPTION :=")[1].strip()
                            
                            # Filter to get text between single quotes
                            if "'" in description:
                                filtered_description = description.split("'")[1]  # Get the text between the quotes
                                log_levels[log_level].append(f"//   - {filtered_description}")

        # Prepare results for the current file
        results = [f"{filename}\n", "// Implemented logging:\n"]
        
        # Write the sorted log levels and descriptions for this file based on custom order
        for level in log_level_order:
            if level in log_levels:  # Check if there are any messages for this log level
                results.append(f"// - {level}:\n")  # Log level header with colon
                for desc in log_levels[level]:
                    results.append(f"{desc}\n")  # Write each description indented

        all_results.extend(results)  # Add current file results to all results
        all_results.append("\n")  # Add an empty line before the next file

# Write all results to the output file
with open(output_file_path, 'w') as output_file:
    output_file.writelines(all_results)

print(f"Results written to {output_file_path}.")
