import pandas as pd
import os

def consolidate_excel_sheets(input_file_paths, sheet_name, output_file_path):
    """
    Extracts a specific sheet from multiple Excel files and consolidates the data
    into a single CSV file.

    Args:
        input_file_paths (list): A list of paths to the input Excel files.
        sheet_name (str): The name of the sheet to extract from each file (e.g., "B2B").
        output_file_path (str): The path where the consolidated CSV file will be saved.
    """
    all_data_frames = []
    
    print(f"Starting consolidation of sheet '{sheet_name}' from {len(input_file_paths)} files...")

    for file_path in input_file_paths:
        if not os.path.exists(file_path):
            print(f"Warning: File not found - {file_path}. Skipping.")
            continue
        
        try:
            # Read the specified sheet from the current Excel file
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            all_data_frames.append(df)
            print(f"Successfully extracted '{sheet_name}' from {os.path.basename(file_path)}")
        except ValueError as e:
            print(f"Error: Sheet '{sheet_name}' not found in {os.path.basename(file_path)}. Skipping. Details: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while processing {os.path.basename(file_path)}: {e}")

    if not all_data_frames:
        print("No data frames were successfully extracted. Output file will not be created.")
        return

    # Concatenate all data frames into a single data frame
    consolidated_df = pd.concat(all_data_frames, ignore_index=True)

    # Save the consolidated data to a new CSV file
    try:
        consolidated_df.to_csv(output_file_path, index=False) # Changed to to_csv
        print(f"\nConsolidation complete! All data saved to: {output_file_path}")
        print(f"Total rows consolidated: {len(consolidated_df)}")
    except Exception as e:
        print(f"Error saving consolidated file to {output_file_path}: {e}")

# --- Example Usage ---
if __name__ == "__main__":
    # Define the directory where your input Excel files are located
    # "." signifies the current directory where the script is run.
    input_directory = "." 
    
    # List of your 12 input Excel file names
    # Replace these with your actual file names (e.g., 'report_jan.xlsx', 'report_feb.xlsx')
    input_file_names = [f"input_file_{i}.xlsx" for i in range(1, 13)] 
    
    # Construct full paths for input files
    input_files = [os.path.join(input_directory, name) for name in input_file_names]

    # The name of the sheet you want to extract
    sheet_to_extract = "B2B"

    # The path for the consolidated output CSV file (changed extension to .csv)
    output_csv_file = "consolidated_b2b_data.csv"

    # Call the function to perform the consolidation
    consolidate_excel_sheets(input_files, sheet_to_extract, output_csv_file)

    # Example for creating dummy files for testing (optional)
    # Uncomment the following block to create dummy files for testing purposes
    """
    print("\nCreating dummy Excel files for testing...")
    os.makedirs(input_directory, exist_ok=True) # Ensure current directory exists (though it always will)
    for i, file_name in enumerate(input_file_names):
        dummy_data_b2b = pd.DataFrame({
            'CustomerID': [101 + i, 102 + i],
            'ProductName': [f'Product A{i}', f'Product B{i}'],
            'Quantity': [5, 12],
            'Price': [10.50, 25.00],
            'Date': [f'2023-01-{i+1:02d}', f'2023-01-{i+2:02d}']
        })
        dummy_data_other = pd.DataFrame({
            'OtherData': ['X', 'Y'],
            'Value': [100, 200]
        })
        
        with pd.ExcelWriter(os.path.join(input_directory, file_name)) as writer:
            dummy_data_b2b.to_excel(writer, sheet_name='B2B', index=False)
            dummy_data_other.to_excel(writer, sheet_name='OtherSheet', index=False)
        print(f"Created dummy file: {file_name}")
    print("Dummy files created. You can now run the consolidation script.")
    """
