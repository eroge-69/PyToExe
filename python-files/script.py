import pandas as pd
import os
import glob

def fix_csv_file(input_file, output_file):

    df = pd.read_csv(input_file)
    
    print(f"Processing: {os.path.basename(input_file)}")
    print(f"  Data rows: {len(df)} (Total lines with header: {len(df) + 1})")
    
    # check 24 data rows = 25 total lines with header
    if len(df) <= 24:
        print(f"  Status: Already correct (24 or fewer data rows)")
        # Copy the file
        df.to_csv(output_file, index=False)
        print(f"  Copied to: {output_file}\n")
        return df
    
    print(f"  Status: Needs correction")
    
    # every 5th row starting from index 4
    corrected_df = df.iloc[4::5].copy()
    print(f"  Step 1: Extracted every 5th row → {len(corrected_df)} data rows")
    
    # Renumber column from 0 to 23
    corrected_df['Hour'] = range(len(corrected_df))
    print(f"  Step 2: Renumbered Hour column → 0 to {len(corrected_df)-1}")
    
    # Save
    corrected_df.to_csv(output_file, index=False)
    print(f"  Saved to: {output_file}")
    print(f"  Final: {len(corrected_df)} data rows ({len(corrected_df) + 1} lines with header)\n")
    
    return corrected_df


def process_folder(source_folder, fixed_folder):
    
    os.makedirs(fixed_folder, exist_ok=True)
    csv_files = glob.glob(os.path.join(source_folder, "*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {source_folder}")
        return
    
    print("="*70)
    print(f"CSV FILE CORRECTION TOOL")
    print("="*70)
    print(f"Source folder: {source_folder}")
    print(f"Fixed folder: {fixed_folder}")
    print(f"Files found: {len(csv_files)}\n")
    
    # Process each CSV file
    success_count = 0
    error_count = 0
    
    for input_file in csv_files:
        try:
            # Get the filename
            filename = os.path.basename(input_file)
            
            # Create output path with same filename in fixed folder
            output_file = os.path.join(fixed_folder, filename)
            
            # Fix the file
            fix_csv_file(input_file, output_file)
            success_count += 1
            
        except Exception as e:
            print(f"  ERROR processing {filename}: {str(e)}\n")
            error_count += 1
    
    # Summary
    print("="*70)
    print("PROCESSING COMPLETE")
    print("="*70)
    print(f"Successfully processed: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Total: {len(csv_files)}")


if __name__ == "__main__":
    # Configure your folder paths here
    SOURCE_FOLDER = "source"      # Folder with original CSV files
    FIXED_FOLDER = "fixed"        # Folder for corrected CSV files
    
    # Run the processing
    process_folder(SOURCE_FOLDER, FIXED_FOLDER)
