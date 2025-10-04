import pandas as pd
import os
import sys

def split_excel_to_csv(input_file):
    if not os.path.exists(input_file):
        print("File not found. Please make sure the file path is correct.")
        return

    # Get the base filename without extension
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    # Load only the first sheet
    df = pd.read_excel(input_file, sheet_name=0)

    # Chunk size
    chunk_size = 500

    # Split and save into multiple CSV files
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i+chunk_size]
        chunk.to_csv(f"{base_name}_part_{i//chunk_size + 1}.csv", index=False)

    print("Done! CSV files saved in the same folder.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # File path comes from drag-and-drop or command line argument
        split_excel_to_csv(sys.argv[1])
    else:
        print("Drag and drop an Excel file onto this script to split it.")
