import pandas as pd
import os

# Get the Downloads folder path
downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
csv_file_path = os.path.join(downloads_path, "costs.csv")

# Read the CSV file
df = pd.read_csv(csv_file_path)

# Generate Excel file in the same Downloads folder
excel_file_path = os.path.join(downloads_path, "teste.xlsx")
df.to_excel(excel_file_path, index=False)

print(f"Excel file created successfully at: {excel_file_path}")