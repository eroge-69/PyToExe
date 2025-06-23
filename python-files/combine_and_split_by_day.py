
import os
import pandas as pd
from io import StringIO

# Define the header line to identify where data starts
HEADER_LINE = 'Date;Time;TxOn;RMS W,;Battery;Temp;'

# Get all .TXT files in the current directory
txt_files = [f for f in os.listdir() if f.lower().endswith('.txt')]

# Initialize a list to collect all data
all_data = []

# Process each file
for file in txt_files:
    with open(file, 'r', encoding='ISO-8859-1') as f:
        lines = f.readlines()
        # Find the index of the header line
        start_index = next((i for i, line in enumerate(lines) if HEADER_LINE in line), None)
        if start_index is not None:
            # Read the data from the header line onward
            data_lines = lines[start_index:]
            # Convert to DataFrame
            df = pd.read_csv(StringIO(''.join(data_lines)), sep=';', engine='python')
            all_data.append(df)

# Combine all data into a single DataFrame
combined_df = pd.concat(all_data, ignore_index=True)

# Save all data to an Excel file with a sheet named 'All_Data'
output_excel = 'Combined_Data_By_Day.xlsx'
with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
    combined_df.to_excel(writer, sheet_name='All_Data', index=False)

    # Ensure 'Date' column is in datetime format
    combined_df['Date'] = pd.to_datetime(combined_df['Date'], errors='coerce', dayfirst=True).dt.date

    # Group by unique dates and write each group to a separate sheet
    for date, group in combined_df.groupby('Date'):
        sheet_name = str(date)
        group.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"Data from {len(txt_files)} files has been combined and saved to '{output_excel}' with separate sheets for each day.")
