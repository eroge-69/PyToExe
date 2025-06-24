import pandas as pd
import sys
import os

def process_excel_file(input_file_path):
    """
    Process Excel file to remove rows based on roll numbers in To_remove column
    """
    try:
        # Read the Excel file from Sheet1 specifically
        print(f"Reading Excel file: {input_file_path} (Sheet1)")
        df = pd.read_excel(input_file_path, sheet_name='Sheet1')
        
        # Display basic info about the file
        print(f"Original data shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print("\nFirst few rows:")
        print(df.head())
        
        # Check if required columns exist
        if 'Roll_no' not in df.columns or 'To_remove' not in df.columns:
            print("Error: Required columns 'Roll_no' and/or 'To_remove' not found in the file")
            print(f"Available columns: {list(df.columns)}")
            return
        
        # Get roll numbers to remove (excluding NaN values)
        roll_numbers_to_remove = df['To_remove'].dropna().unique()
        print(f"\nRoll numbers to remove: {roll_numbers_to_remove}")
        
        # Remove rows where Roll_no matches any roll number in To_remove column
        initial_count = len(df)
        df_cleaned = df[~df['Roll_no'].isin(roll_numbers_to_remove)]
        final_count = len(df_cleaned)
        
        print(f"\nRows removed: {initial_count - final_count}")
        print(f"Remaining rows: {final_count}")
        
        # Create output filename
        base_name = os.path.splitext(input_file_path)[0]
        output_file_path = f"{base_name}_cleaned.xlsx"
        
        # Save the cleaned data to Sheet1
        df_cleaned.to_excel(output_file_path, sheet_name='Sheet1', index=False)
        print(f"\nCleaned data saved to: {output_file_path}")
        
        # Display summary of cleaned data
        print("\nCleaned data summary:")
        print(f"Shape: {df_cleaned.shape}")
        print("\nFirst few rows of cleaned data:")
        print(df_cleaned.head())
        
        return output_file_path
        
    except FileNotFoundError:
        print(f"Error: File '{input_file_path}' not found")
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return None

if __name__ == "__main__":
    input_file = r"e:\m_ali\GradeWiseReport (19).xlsx"
    
    if os.path.exists(input_file):
        process_excel_file(input_file)
    else:
        print(f"File not found: {input_file}")
