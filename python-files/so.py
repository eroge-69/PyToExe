import os
import pandas as pd

# Define the root directory containing folders
root_dir = 'path/to/your/root/folder'

# List to hold all dataframes
all_data = []

# Walk through all folders and files
for subdir, _, files in os.walk(root_dir):
    for file in files:
        if file.endswith('.xlsx') or file.endswith('.xls'):
            file_path = os.path.join(subdir, file)
            try:
                df = pd.read_excel(file_path)
                # Optionally, add columns to track source file info
                df['Source_File'] = file
                all_data.append(df)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

# Concatenate all dataframes
combined_df = pd.concat(all_data, ignore_index=True)

# Save combined data to a new Excel file
combined_df.to_excel('combined_data.xlsx', index=False)

# Now you can filter, analyze, or create new files from combined_df